import Parameters
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-! The unchanged whole-machine target, including visited space. It is a
definition, not a proved theorem. No local theorem below inhabits `Complete`.

A program has a fixed finite alphabet, fixed finite control and fixed number
of tapes. Its transition table sees only control and scanned symbols. Input
bits occupy tapes 0 and 1; the product is returned on tape 2, MSB first with
exactly 2n bits. Cells are indexed by integers, and a transition moves each
head by at most one. A halted execution stutters; its first halt is therefore
no later than any accepted witness time.
-/
namespace WholeMachine.Target

inductive Motion where
  | left | stay | right
  deriving DecidableEq

def Motion.displacement : Motion → ℤ
  | .left => -1
  | .stay => 0
  | .right => 1

structure Program (work control extra : ℕ) where
  initial : Fin control
  table : Fin control → (Fin (work + 3) → Fin (extra + 3)) →
    Option (Fin control × (Fin (work + 3) → Fin (extra + 3) × Motion))

structure Configuration (work control extra : ℕ) where
  state : Fin control
  head : Fin (work + 3) → ℤ
  cells : Fin (work + 3) → ℤ → Fin (extra + 3)

variable {w c a : ℕ}

def scanned (s : Configuration w c a) : Fin (w + 3) → Fin (a + 3) :=
  fun i => s.cells i (s.head i)

def step (P : Program w c a) (s : Configuration w c a) : Configuration w c a :=
  match P.table s.state (scanned s) with
  | none => s
  | some (next, actions) => {
      state := next
      head := fun i => s.head i + (actions i).2.displacement
      cells := fun i j => if j = s.head i then (actions i).1 else s.cells i j }

def halted (P : Program w c a) (s : Configuration w c a) : Prop :=
  P.table s.state (scanned s) = none

def run (P : Program w c a) (s : Configuration w c a) : ℕ → Configuration w c a
  | 0 => s
  | k + 1 => step P (run P s k)

def bit (b : Bool) : Fin (a + 3) := ⟨if b then 2 else 1, by split <;> omega⟩

def word (bs : List Bool) (j : ℤ) : Fin (a + 3) :=
  if 0 ≤ j then (bs[j.toNat]?.map bit).getD 0 else 0

def input (P : Program w c a) (x y : List Bool) : Configuration w c a where
  state := P.initial
  head := fun _ => 0
  cells := fun i => if i.val = 0 then word x else if i.val = 1 then word y else fun _ => 0

def value : List Bool → ℕ
  | [] => 0
  | b :: bs => (if b then 1 else 0) * 2 ^ bs.length + value bs

def output (n : ℕ) (x y : List Bool) (s : Configuration w c a) : Prop :=
  ∃ z : List Bool, z.length = 2 * n ∧ value z = value x * value y ∧
    s.cells ⟨2, by omega⟩ = word z

/-- All cells scanned in a configuration, tagged by tape. -/
def heads (s : Configuration w c a) : Finset (Fin (w + 3) × ℤ) :=
  Finset.univ.image fun i => (i, s.head i)

/-- Count the entire execution, not only the nonblank cells at return. -/
def visited (P : Program w c a) (s : Configuration w c a) : ℕ → Finset (Fin (w + 3) × ℤ)
  | 0 => heads s
  | k + 1 => visited P s k ∪ heads (run P s (k + 1))

/-- Input storage counts even before the machine has scanned it. -/
def initialStorage (n : ℕ) : Finset (Fin (w + 3) × ℤ) :=
  ((Finset.range n).image fun (j : ℕ) => (⟨0, by omega⟩, (j : ℤ))) ∪
  ((Finset.range n).image fun (j : ℕ) => (⟨1, by omega⟩, (j : ℤ)))

noncomputable def timeScale (n : ℕ) : ℝ :=
  (n : ℝ) * (Real.log (max 2 n : ℕ) / Real.log 2) ^ (1 - (Parameters.kappa : ℝ))

/-- The exact desired result. All witnesses precede all inputs. No supplier,
analytic, cost, or space contract is assumed in this proposition. -/
def Complete : Prop :=
  ∃ (w c a : ℕ) (P : Program w c a) (C : ℝ), 0 < C ∧
    ∀ (n : ℕ), 1 ≤ n → ∀ (x y : List Bool), x.length = n → y.length = n →
      ∃ k : ℕ,
        halted P (run P (input P x y) k) ∧
        output n x y (run P (input P x y) k) ∧
        (k : ℝ) ≤ C * timeScale n ∧
        ((visited P (input P x y) k ∪ initialStorage n).card : ℝ) ≤ C * n

theorem step_moves_at_most_one (P : Program w c a) (s : Configuration w c a)
    (i : Fin (w + 3)) :
    -1 ≤ (step P s).head i - s.head i ∧ (step P s).head i - s.head i ≤ 1 := by
  unfold step
  split
  · simp
  · rename_i next actions h
    simp only
    cases (actions i).2 <;> simp [Motion.displacement]

theorem step_preserves_unscanned (P : Program w c a) (s : Configuration w c a)
    (i : Fin (w + 3)) (j : ℤ) (hj : j ≠ s.head i) :
    (step P s).cells i j = s.cells i j := by
  unfold step
  split <;> simp_all

theorem visited_mono (P : Program w c a) (s : Configuration w c a) :
    Monotone (visited P s) := by
  apply monotone_nat_of_le_succ
  intro k
  exact Finset.subset_union_left

theorem run_add (P : Program w c a) (s : Configuration w c a) (k l : ℕ) :
    run P s (k + l) = run P (run P s k) l := by
  induction l with
  | zero => rfl
  | succ l ih =>
    change step P (run P s (k + l)) = step P (run P (run P s k) l)
    exact congrArg (step P) ih

theorem halted_step (P : Program w c a) (s : Configuration w c a) (h : halted P s) :
    step P s = s := by
  unfold step
  rw [h]

theorem run_after_halt (P : Program w c a) (s : Configuration w c a)
    (k l : ℕ) (h : halted P (run P s k)) : run P s (k + l) = run P s k := by
  rw [run_add]
  induction l with
  | zero => rfl
  | succ l ih => rw [run, ih, halted_step P _ h]

/-- An arbitrary halting witness can be replaced by the first halt, without
changing the returned configuration or increasing the number of transitions. -/
theorem first_halt (P : Program w c a) (s : Configuration w c a)
    (k : ℕ) (h : halted P (run P s k)) :
    ∃ j ≤ k, halted P (run P s j) ∧ (∀ i < j, ¬ halted P (run P s i)) ∧
      run P s j = run P s k := by
  classical
  let hex : ∃ j, halted P (run P s j) := ⟨k, h⟩
  let j := Nat.find hex
  have hj : j ≤ k := Nat.find_min' hex h
  have hh : halted P (run P s j) := Nat.find_spec hex
  refine ⟨j, hj, hh, fun i hi => Nat.find_min hex hi, ?_⟩
  have he := run_after_halt P s j (k - j) hh
  rw [Nat.add_sub_of_le hj] at he
  exact he.symm

theorem heads_subset_visited (P : Program w c a) (s : Configuration w c a) (k : ℕ) :
    heads (run P s k) ⊆ visited P s k := by
  cases k with
  | zero => exact Finset.Subset.refl _
  | succ k => exact Finset.subset_union_right

/-- Exact visited-space composition, retaining the earlier visited region. -/
theorem visited_add (P : Program w c a) (s : Configuration w c a) (k l : ℕ) :
    visited P s (k + l) = visited P s k ∪ visited P (run P s k) l := by
  induction l with
  | zero =>
    simp only [Nat.add_zero, visited]
    exact (Finset.union_eq_left.mpr (heads_subset_visited P s k)).symm
  | succ l ih =>
    change visited P s (k + l) ∪ heads (run P s (k + (l + 1))) =
      visited P s k ∪ (visited P (run P s k) l ∪ heads (run P (run P s k) (l + 1)))
    rw [ih, run_add, Finset.union_assoc]

/-- A cell outside the scanned region cannot be modified, even if a later
phase erases every work tape. -/
theorem unvisited_unchanged (P : Program w c a) (s : Configuration w c a)
    (k : ℕ) (i : Fin (w + 3)) (j : ℤ) (hj : (i, j) ∉ visited P s k) :
    (run P s k).cells i j = s.cells i j := by
  induction k with
  | zero => rfl
  | succ k ih =>
    have hold : (i, j) ∉ visited P s k :=
      fun hm => hj (Finset.mem_union_left _ hm)
    have hhead : j ≠ (run P s k).head i := by
      intro he
      apply hold
      apply heads_subset_visited P s k
      exact Finset.mem_image.mpr ⟨i, Finset.mem_univ _, by simp [he]⟩
    rw [run, step_preserves_unscanned P _ i j hhead]
    exact ih hold

theorem value_lt (bs : List Bool) : value bs < 2 ^ bs.length := by
  induction bs with
  | nil => decide
  | cons b bs ih =>
    cases b <;> simp only [value, List.length_cons, pow_succ,
      Bool.false_eq_true, ↓reduceIte, zero_mul, one_mul, zero_add] <;> omega

end WholeMachine.Target
