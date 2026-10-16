import BoundedCalls
import Mathlib.Analysis.Normed.Operator.Prod
import Mathlib.Analysis.Normed.Operator.ContinuousLinearMap

/-! Two sources of contiguous-subword bounds used in the written proof:
invertible prefixes and augmented Horner state. Neither relies on the norm of
the completed operator alone. -/
namespace WholeMachine.Intervals

open BoundedCalls

variable {V : Type*} [NormedAddCommGroup V] [NormedSpace ℝ V]

def fromPrefixes (P : ℕ → V ≃L[ℝ] V) (i : ℕ) : V →L[ℝ] V :=
  (P (i + 1)).toContinuousLinearMap.comp (P i).symm.toContinuousLinearMap

theorem segment_fromPrefixes (P : ℕ → V ≃L[ℝ] V) (s l : ℕ) (x : V) :
    segment (fromPrefixes P) s l x = P (s + l) ((P s).symm x) := by
  induction l with
  | zero => simp
  | succ l ih =>
    simp only [segment_succ, ih, fromPrefixes, ContinuousLinearMap.comp_apply,
      ContinuousLinearEquiv.coe_coe, ContinuousLinearEquiv.symm_apply_apply]
    rfl

/-- Prefix and inverse-prefix envelopes give the interval envelope `K²`. -/
theorem inverse_prefix_interval (P : ℕ → V ≃L[ℝ] V) (s l : ℕ) (K : ℝ)
    (hK : 0 ≤ K)
    (hp : ∀ v : V, ‖P (s + l) v‖ ≤ K * ‖v‖)
    (hi : ∀ v : V, ‖(P s).symm v‖ ≤ K * ‖v‖) (x : V) :
    ‖segment (fromPrefixes P) s l x‖ ≤ K ^ 2 * ‖x‖ := by
  rw [segment_fromPrefixes]
  calc
    _ ≤ K * ‖(P s).symm x‖ := hp _
    _ ≤ K * (K * ‖x‖) := mul_le_mul_of_nonneg_left (hi x) hK
    _ = _ := by ring

/-- The input is retained while the accumulator receives `Q acc + B input`.
This map is allowed to be singular. The product has the supremum norm. -/
def horner (Q B : V →L[ℝ] V) : (V × V) →L[ℝ] (V × V) :=
  (ContinuousLinearMap.fst ℝ V V).prod
    (Q.comp (ContinuousLinearMap.snd ℝ V V) + B.comp (ContinuousLinearMap.fst ℝ V V))

@[simp] theorem horner_apply (Q B : V →L[ℝ] V) (v : V × V) :
    horner Q B v = (v.1, Q v.2 + B v.1) := rfl

theorem horner_fst (Q B : ℕ → V →L[ℝ] V) (s l : ℕ) (v : V × V) :
    (segment (fun i => horner (Q i) (B i)) s l v).1 = v.1 := by
  induction l with
  | zero => rfl
  | succ l ih => simpa only [segment_succ, horner_apply] using ih

/-- A subword of length `l` grows the accumulator additively, not by a
product of one-step upper bounds. -/
theorem horner_snd (Q B : ℕ → V →L[ℝ] V) (L : ℝ)
    (hQ : ∀ i v, ‖Q i v‖ ≤ ‖v‖) (hB : ∀ i v, ‖B i v‖ ≤ L * ‖v‖)
    (s l : ℕ) (v : V × V) :
    ‖(segment (fun i => horner (Q i) (B i)) s l v).2‖ ≤
      ‖v.2‖ + (l : ℝ) * L * ‖v.1‖ := by
  induction l with
  | zero => simp
  | succ l ih =>
    simp only [segment_succ, horner_apply]
    calc
      _ ≤ ‖Q (s + l) (segment (fun i => horner (Q i) (B i)) s l v).2‖ +
          ‖B (s + l) (segment (fun i => horner (Q i) (B i)) s l v).1‖ := norm_add_le _ _
      _ ≤ ‖(segment (fun i => horner (Q i) (B i)) s l v).2‖ +
          L * ‖(segment (fun i => horner (Q i) (B i)) s l v).1‖ :=
        add_le_add (hQ _ _) (hB _ _)
      _ ≤ (‖v.2‖ + (l : ℝ) * L * ‖v.1‖) + L * ‖v.1‖ := by
        rw [horner_fst]
        exact add_le_add ih le_rfl
      _ = _ := by push_cast; ring

theorem horner_interval (Q B : ℕ → V →L[ℝ] V) (L : ℝ) (hL : 0 ≤ L)
    (hQ : ∀ i v, ‖Q i v‖ ≤ ‖v‖) (hB : ∀ i v, ‖B i v‖ ≤ L * ‖v‖)
    (s l : ℕ) (v : V × V) :
    ‖segment (fun i => horner (Q i) (B i)) s l v‖ ≤ (1 + (l : ℝ) * L) * ‖v‖ := by
  rw [Prod.norm_def, max_le_iff]
  constructor
  · rw [horner_fst]
    calc
      _ ≤ ‖v‖ := norm_fst_le v
      _ ≤ _ := by
        nlinarith [mul_nonneg (mul_nonneg (Nat.cast_nonneg (α := ℝ) l) hL) (norm_nonneg v)]
  · calc
      _ ≤ ‖v.2‖ + (l : ℝ) * L * ‖v.1‖ := horner_snd Q B L hQ hB s l v
      _ ≤ ‖v‖ + (l : ℝ) * L * ‖v‖ := by
        exact add_le_add (norm_snd_le v)
          (mul_le_mul_of_nonneg_left (norm_fst_le v) (by positivity))
      _ = _ := by ring

end WholeMachine.Intervals
