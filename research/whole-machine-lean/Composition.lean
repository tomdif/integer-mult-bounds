import Target

/-! Literal composition of two finite transition tables on shared tapes.
The handoff is one charged, head-local transition. No subroutine-call oracle
or unit-cost arithmetic operation is added to the machine model. -/
namespace WholeMachine.Composition

open Target

variable {w a c d : ℕ}

def left (s : Configuration w c a) : Configuration w (c + d) a where
  state := s.state.castAdd d
  head := s.head
  cells := s.cells

def right (s : Configuration w d a) : Configuration w (c + d) a where
  state := s.state.natAdd c
  head := s.head
  cells := s.cells

def restart (Q : Program w d a) (s : Configuration w c a) : Configuration w d a where
  state := Q.initial
  head := s.head
  cells := s.cells

def sequence (P : Program w c a) (Q : Program w d a) : Program w (c + d) a where
  initial := P.initial.castAdd d
  table := Fin.addCases
    (fun q tape => match P.table q tape with
      | none => some (Q.initial.natAdd c, fun i => (tape i, .stay))
      | some (next, action) => some (next.castAdd d, action))
    (fun q tape => (Q.table q tape).map fun (next, action) => (next.natAdd c, action))

theorem left_step (P : Program w c a) (Q : Program w d a) (s : Configuration w c a)
    (h : ¬ halted P s) : step (sequence P Q) (left s) = left (step P s) := by
  unfold halted at h
  simp only [step, sequence, left, scanned, Fin.addCases_left]
  unfold Target.scanned
  cases he : P.table s.state (fun i => s.cells i (s.head i)) with
  | none => exact (h he).elim
  | some result => rcases result with ⟨next, action⟩; rfl

theorem right_step (P : Program w c a) (Q : Program w d a) (s : Configuration w d a) :
    step (sequence P Q) (right s) = right (step Q s) := by
  simp only [step, sequence, right, Fin.addCases_right]
  unfold Target.scanned
  cases he : Q.table s.state (fun i => s.cells i (s.head i)) with
  | none => rfl
  | some result => rcases result with ⟨next, action⟩; rfl

theorem handoff (P : Program w c a) (Q : Program w d a) (s : Configuration w c a)
    (h : halted P s) : step (sequence P Q) (left s) = right (restart Q s) := by
  unfold halted scanned at h
  simp only [step, sequence, left, scanned, Fin.addCases_left, right, restart]
  unfold Target.scanned
  rw [h]
  simp only [Motion.displacement, add_zero]
  congr 1
  funext i j
  split <;> simp_all

theorem run_left (P : Program w c a) (Q : Program w d a) (s : Configuration w c a)
    (k : ℕ) (h : ∀ j < k, ¬ halted P (run P s j)) :
    run (sequence P Q) (left s) k = left (run P s k) := by
  induction k with
  | zero => rfl
  | succ k ih =>
    rw [run, ih (fun j hj => h j (by omega)), left_step P Q _ (h k (by omega))]
    rfl

theorem run_right (P : Program w c a) (Q : Program w d a) (s : Configuration w d a)
    (k : ℕ) : run (sequence P Q) (right s) k = right (run Q s k) := by
  induction k with
  | zero => rfl
  | succ k ih => rw [run, ih, right_step]; rfl

/-- Exact time accounting: `k` steps, one handoff, then `l` steps. -/
theorem run_sequence (P : Program w c a) (Q : Program w d a) (s : Configuration w c a)
    (k l : ℕ) (hfirst : ∀ j < k, ¬ halted P (run P s j))
    (hhalt : halted P (run P s k)) :
    run (sequence P Q) (left s) (k + 1 + l) =
      right (run Q (restart Q (run P s k)) l) := by
  rw [run_add, run, run_left P Q s k hfirst, handoff P Q _ hhalt, run_right]

theorem visited_left (P : Program w c a) (Q : Program w d a) (s : Configuration w c a)
    (k : ℕ) (h : ∀ j < k, ¬ halted P (run P s j)) :
    visited (sequence P Q) (left s) k = visited P s k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    rw [visited, ih (fun j hj => h j (by omega)), run_left P Q s (k + 1) h]
    rfl

theorem visited_right (P : Program w c a) (Q : Program w d a) (s : Configuration w d a)
    (k : ℕ) : visited (sequence P Q) (right s) k = visited Q s k := by
  induction k with
  | zero => rfl
  | succ k ih => rw [visited, ih, run_right]; rfl

/-- The handoff visits no new cell. The footprint is the union of the two
real execution footprints, including cells erased before either return. -/
theorem visited_sequence (P : Program w c a) (Q : Program w d a) (s : Configuration w c a)
    (k l : ℕ) (hfirst : ∀ j < k, ¬ halted P (run P s j))
    (hhalt : halted P (run P s k)) :
    visited (sequence P Q) (left s) (k + 1 + l) =
      visited P s k ∪ visited Q (restart Q (run P s k)) l := by
  rw [visited_add, visited, visited_left P Q s k hfirst,
    run, run_left P Q s k hfirst, handoff P Q _ hhalt, visited_right]
  have hh : heads (right (restart Q (run P s k)) : Configuration w (c + d) a) =
      heads (run P s k) := rfl
  rw [hh, Finset.union_eq_left.mpr (heads_subset_visited P s k)]

theorem space_sequence (P : Program w c a) (Q : Program w d a) (s : Configuration w c a)
    (k l : ℕ) (hfirst : ∀ j < k, ¬ halted P (run P s j))
    (hhalt : halted P (run P s k)) :
    (visited (sequence P Q) (left s) (k + 1 + l)).card ≤
      (visited P s k).card + (visited Q (restart Q (run P s k)) l).card := by
  rw [visited_sequence P Q s k l hfirst hhalt]
  exact Finset.card_union_le _ _

theorem right_halted (P : Program w c a) (Q : Program w d a) (s : Configuration w d a)
    (h : halted Q s) : halted (sequence P Q) (right s) := by
  unfold halted at *
  simp only [sequence, right, Fin.addCases_right, Option.map_eq_none_iff]
  unfold Target.scanned at *
  exact h

/-- Composition accepts any halting witness, including one padded by stutter
steps. The theorem derives the first halt internally; no such caller premise
is needed. Both time and visited-space bounds refer to the literal machine. -/
theorem compose_halting_runs (P : Program w c a) (Q : Program w d a)
    (s : Configuration w c a) (k l : ℕ)
    (hP : halted P (run P s k))
    (hQ : halted Q (run Q (restart Q (run P s k)) l)) :
    ∃ t ≤ k + 1 + l,
      run (sequence P Q) (left s) t = right (run Q (restart Q (run P s k)) l) ∧
      halted (sequence P Q) (run (sequence P Q) (left s) t) ∧
      visited (sequence P Q) (left s) t ⊆
        visited P s k ∪ visited Q (restart Q (run P s k)) l := by
  obtain ⟨j, hj, hhalt, hfirst, hstate⟩ := first_halt P s k hP
  have hrun := run_sequence P Q s j l hfirst hhalt
  rw [hstate] at hrun
  refine ⟨j + 1 + l, by omega, hrun, ?_, ?_⟩
  · rw [hrun]
    exact right_halted P Q _ hQ
  · rw [visited_sequence P Q s j l hfirst hhalt, hstate]
    exact Finset.union_subset_union (visited_mono P s hj) (Finset.Subset.refl _)

end WholeMachine.Composition
