import Mathlib.Analysis.Normed.Operator.Basic
import Mathlib.Tactic

/-! Finite noisy linear schedules. The local approximation contract is only
valid on the unit ball. The induction below establishes that every actual
call lies in that ball; this is not an assumption about the executed trace.

There are still hypotheses about the ideal interval operators and the local
implementations. Instantiating these from a finite tape program is separate.
-/
namespace WholeMachine.BoundedCalls

open Finset

variable {V : Type*} [NormedAddCommGroup V] [NormedSpace ℝ V]

/-- The exact chronological subword starting at `start`, with `len` stages. -/
def segment (A : ℕ → V →L[ℝ] V) (start : ℕ) : ℕ → V →L[ℝ] V
  | 0 => ContinuousLinearMap.id ℝ V
  | len + 1 => (A (start + len)).comp (segment A start len)

@[simp] theorem segment_zero (A : ℕ → V →L[ℝ] V) (start : ℕ) (x : V) :
    segment A start 0 x = x := rfl

@[simp] theorem segment_succ (A : ℕ → V →L[ℝ] V) (start len : ℕ) (x : V) :
    segment A start (len + 1) x = A (start + len) (segment A start len x) := rfl

/-- `F` is the actual approximate operation, including its rounding. -/
def execute (F : ℕ → V → V) (x : V) : ℕ → V
  | 0 => x
  | n + 1 => F n (execute F x n)

def residual (A : ℕ → V →L[ℝ] V) (F : ℕ → V → V) (x : V) (i : ℕ) : V :=
  execute F x (i + 1) - A i (execute F x i)

/-- Exact error identity, without any approximation or domain assumptions. -/
theorem error_expansion (A : ℕ → V →L[ℝ] V) (F : ℕ → V → V) (x : V) (n : ℕ) :
    execute F x n - segment A 0 n x =
      ∑ i ∈ range n, segment A (i + 1) (n - (i + 1)) (residual A F x i) := by
  induction n with
  | zero => simp [execute]
  | succ n ih =>
    rw [Finset.sum_range_succ]
    simp only [show n + 1 - (n + 1) = 0 by omega, segment_zero, segment_succ, zero_add]
    have hsum :
        (∑ i ∈ range n, segment A (i + 1) (n + 1 - (i + 1)) (residual A F x i)) =
          A n (∑ i ∈ range n, segment A (i + 1) (n - (i + 1)) (residual A F x i)) := by
      rw [map_sum]
      apply Finset.sum_congr rfl
      intro i hi
      have hi' := Finset.mem_range.mp hi
      have hlen : n + 1 - (i + 1) = (n - (i + 1)) + 1 := by omega
      have hindex : i + 1 + (n - (i + 1)) = n := by omega
      rw [hlen, segment_succ, hindex]
    rw [hsum, ← ih, map_sub]
    simp only [residual]
    abel

/-- With bounded residuals, the interval envelope gives a linear error sum. -/
theorem error_bound (A : ℕ → V →L[ℝ] V) (F : ℕ → V → V) (x : V)
    (n : ℕ) (K η : ℝ) (hK : 0 ≤ K)
    (hinterval : ∀ i < n, ∀ v : V,
      ‖segment A (i + 1) (n - (i + 1)) v‖ ≤ K * ‖v‖)
    (hresidual : ∀ i < n, ‖residual A F x i‖ ≤ η) :
    ‖execute F x n - segment A 0 n x‖ ≤ (n : ℝ) * K * η := by
  rw [error_expansion]
  calc
    _ ≤ ∑ i ∈ range n, ‖segment A (i + 1) (n - (i + 1)) (residual A F x i)‖ :=
      norm_sum_le _ _
    _ ≤ ∑ _i ∈ range n, K * η := by
      apply Finset.sum_le_sum
      intro i hi
      exact (hinterval i (mem_range.mp hi) _).trans
        (mul_le_mul_of_nonneg_left (hresidual i (mem_range.mp hi)) hK)
    _ = _ := by simp; ring

/-- First-failure induction. No premise says that the actual calls are bounded. -/
theorem all_calls_bounded (A : ℕ → V →L[ℝ] V) (F : ℕ → V → V) (x : V)
    (m : ℕ) (K η : ℝ) (hK : 0 ≤ K) (hη : 0 ≤ η)
    (hprefix : ∀ j ≤ m, ‖segment A 0 j x‖ ≤ 1 / 8)
    (hinterval : ∀ j ≤ m, ∀ i < j, ∀ v : V,
      ‖segment A (i + 1) (j - (i + 1)) v‖ ≤ K * ‖v‖)
    (hbudget : (m : ℝ) * K * η ≤ 1 / 8)
    (hlocal : ∀ i < m, ∀ v : V, ‖v‖ ≤ 1 → ‖F i v - A i v‖ ≤ η) :
    ∀ j ≤ m, ‖execute F x j‖ ≤ 1 / 4 ∧
      ‖execute F x j - segment A 0 j x‖ ≤ (j : ℝ) * K * η := by
  intro j
  induction j using Nat.strong_induction_on with
  | h j ih =>
    intro hj
    have he : ‖execute F x j - segment A 0 j x‖ ≤ (j : ℝ) * K * η := by
      apply error_bound A F x j K η hK (hinterval j hj)
      intro i hi
      have hv := (ih i hi (by omega)).1
      exact hlocal i (by omega) _ (by linarith)
    have hjm : (j : ℝ) ≤ m := by exact_mod_cast hj
    have heb : ‖execute F x j - segment A 0 j x‖ ≤ 1 / 8 :=
      he.trans ((by gcongr : (j : ℝ) * K * η ≤ (m : ℝ) * K * η).trans hbudget)
    refine ⟨?_, he⟩
    calc
      ‖execute F x j‖ ≤ ‖execute F x j - segment A 0 j x‖ + ‖segment A 0 j x‖ :=
        norm_le_norm_sub_add _ _
      _ ≤ 1 / 4 := by linarith [hprefix j hj]

def scaleBits (E : ℕ) : ℕ := E + 4

def precisionBits (E Q m : ℕ) : ℕ := Q + scaleBits E + 2 * E + Nat.clog 2 m + 3

/-- Exact dyadic budget; `clog` makes it valid for every number of calls. -/
theorem precision_budget (E Q m : ℕ) :
    (m : ℝ) * 2 ^ (2 * E) * (2 ^ precisionBits E Q m : ℝ)⁻¹ ≤
      (2 ^ (Q + scaleBits E + 3) : ℝ)⁻¹ := by
  have hm : (m : ℝ) ≤ (2 : ℝ) ^ Nat.clog 2 m := by
    exact_mod_cast Nat.le_pow_clog (by decide : 1 < 2) m
  have hpow : (2 : ℝ) ^ precisionBits E Q m =
      2 ^ (Q + scaleBits E + 3) * 2 ^ (2 * E) * 2 ^ Nat.clog 2 m := by
    rw [precisionBits, show Q + scaleBits E + 2 * E + Nat.clog 2 m + 3 =
      (Q + scaleBits E + 3) + 2 * E + Nat.clog 2 m by omega]
    simp only [pow_add]
  calc
    _ ≤ (2 : ℝ) ^ Nat.clog 2 m * 2 ^ (2 * E) * (2 ^ precisionBits E Q m : ℝ)⁻¹ :=
      by gcongr
    _ = _ := by rw [hpow]; field_simp

theorem budget_le_eighth (E Q : ℕ) :
    (2 ^ (Q + scaleBits E + 3) : ℝ)⁻¹ ≤ 1 / 8 := by
  have h : (8 : ℝ) ≤ 2 ^ (Q + scaleBits E + 3) := by
    calc
      (8 : ℝ) = 2 ^ (3 : ℕ) := by norm_num
      _ ≤ _ := by gcongr <;> norm_num
  simpa only [one_div] using inv_anti₀ (by norm_num : (0 : ℝ) < 8) h

theorem scaled_prefix (A : ℕ → V →L[ℝ] V) (x : V) (E j : ℕ)
    (hx : ‖x‖ ≤ 2) (hp : ∀ v : V, ‖segment A 0 j v‖ ≤ (2 : ℝ)^E * ‖v‖) :
    ‖segment A 0 j ((2 ^ scaleBits E : ℝ)⁻¹ • x)‖ ≤ 1 / 8 := by
  rw [map_smul, norm_smul, Real.norm_eq_abs, abs_of_nonneg (by positivity)]
  calc
    _ ≤ (2 ^ scaleBits E : ℝ)⁻¹ * ((2 : ℝ)^E * 2) := by
      apply mul_le_mul_of_nonneg_left _ (by positivity)
      exact (hp x).trans (mul_le_mul_of_nonneg_left hx (by positivity))
    _ = _ := by simp [scaleBits, pow_add]; field_simp; ring

/-- Restore the scale only after all calls; the error allowance includes it. -/
theorem restore_error (A : ℕ → V →L[ℝ] V) (F : ℕ → V → V)
    (x : V) (E Q m : ℕ)
    (herr : ‖execute F ((2 ^ scaleBits E : ℝ)⁻¹ • x) m -
      segment A 0 m ((2 ^ scaleBits E : ℝ)⁻¹ • x)‖ ≤
        (2 ^ (Q + scaleBits E + 3) : ℝ)⁻¹) :
    ‖(2 ^ scaleBits E : ℝ) • execute F ((2 ^ scaleBits E : ℝ)⁻¹ • x) m -
      segment A 0 m x‖ ≤ (2 ^ (Q + 3) : ℝ)⁻¹ := by
  have heq : (2 ^ scaleBits E : ℝ) •
      segment A 0 m ((2 ^ scaleBits E : ℝ)⁻¹ • x) = segment A 0 m x := by
    rw [map_smul, smul_smul]
    simp
  rw [← heq, ← smul_sub, norm_smul, Real.norm_eq_abs, abs_of_nonneg (by positivity)]
  calc
    _ ≤ (2 ^ scaleBits E : ℝ) * (2 ^ (Q + scaleBits E + 3) : ℝ)⁻¹ := by gcongr
    _ = _ := by simp [pow_add]; field_simp

/-- The full bounded-call rescaling lemma, universally quantified over the
stage count and the normed space (including padded rectangular stages).
The operator envelopes and the individual implementation contract are explicit.
-/
theorem scaled_schedule (A : ℕ → V →L[ℝ] V) (F : ℕ → V → V)
    (x : V) (E Q m : ℕ) (hx : ‖x‖ ≤ 2)
    (hprefix : ∀ j ≤ m, ∀ v : V, ‖segment A 0 j v‖ ≤ (2 : ℝ)^E * ‖v‖)
    (hinterval : ∀ j ≤ m, ∀ i < j, ∀ v : V,
      ‖segment A (i + 1) (j - (i + 1)) v‖ ≤ (2 : ℝ)^(2*E) * ‖v‖)
    (hlocal : ∀ i < m, ∀ v : V, ‖v‖ ≤ 1 →
      ‖F i v - A i v‖ ≤ (2 ^ precisionBits E Q m : ℝ)⁻¹) :
    (∀ j ≤ m, ‖execute F ((2 ^ scaleBits E : ℝ)⁻¹ • x) j‖ ≤ 1 / 4) ∧
    ‖(2 ^ scaleBits E : ℝ) • execute F ((2 ^ scaleBits E : ℝ)⁻¹ • x) m -
      segment A 0 m x‖ ≤ (2 ^ (Q + 3) : ℝ)⁻¹ := by
  have hb := all_calls_bounded A F ((2 ^ scaleBits E : ℝ)⁻¹ • x) m
    ((2 : ℝ)^(2*E)) ((2 ^ precisionBits E Q m : ℝ)⁻¹)
    (by positivity) (by positivity)
    (fun j hj => scaled_prefix A x E j hx (hprefix j hj))
    hinterval ((precision_budget E Q m).trans (budget_le_eighth E Q)) hlocal
  refine ⟨fun j hj => (hb j hj).1, ?_⟩
  apply restore_error A F x E Q m
  exact (hb m le_rfl).2.trans (precision_budget E Q m)

omit [NormedSpace ℝ V] in
/-- Optional final rounding uses the remaining error budget. -/
theorem final_rounding (Q : ℕ) (ideal restored rounded : V)
    (hr : ‖restored - ideal‖ ≤ (2 ^ (Q + 3) : ℝ)⁻¹)
    (hq : ‖rounded - restored‖ ≤ (2 ^ (Q + 2) : ℝ)⁻¹) :
    ‖rounded - ideal‖ < (2 ^ Q : ℝ)⁻¹ := by
  calc
    _ ≤ ‖rounded - restored‖ + ‖restored - ideal‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ (2 ^ (Q + 2) : ℝ)⁻¹ + (2 ^ (Q + 3) : ℝ)⁻¹ := add_le_add hq hr
    _ < _ := by
      simp only [pow_add]
      have hp : (0 : ℝ) < 2 ^ Q := by positivity
      field_simp
      norm_num

end WholeMachine.BoundedCalls
