import Parameters
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics
import Mathlib.Analysis.Asymptotics.Lemmas

/-! Asymptotic arithmetic only: no operation-count assertion is introduced. -/
namespace WholeMachine.Costs

open Filter Asymptotics

theorem absorb_polylog (a b d : ℝ) (hab : a < b) :
    (fun p : ℝ => p ^ a * Real.log p ^ d) =o[atTop] (fun p : ℝ => p ^ b) := by
  have h := (isBigO_refl (fun p : ℝ => p ^ a) atTop).mul_isLittleO
    (isLittleO_log_rpow_rpow_atTop d (sub_pos.mpr hab))
  apply h.congr' (Filter.Eventually.of_forall fun _ => rfl)
  filter_upwards [eventually_gt_atTop (0 : ℝ)] with p hp
  rw [← Real.rpow_add hp]
  congr 1
  ring

theorem cost_row_absorbed (row : Parameters.CostRow) (d : ℝ) :
    (fun p : ℝ => p ^ (Parameters.costPower row : ℝ) * Real.log p ^ d) =o[atTop]
      (fun p : ℝ => p ^ (1 - (Parameters.kappa : ℝ))) := by
  apply absorb_polylog
  exact_mod_cast Parameters.all_cost_powers_lt row

theorem guard_envelope_sublinear (d : ℝ) :
    (fun p : ℝ => p ^ (Parameters.beta : ℝ) * Real.log p ^ d +
      p ^ ((Parameters.beta : ℝ) + 2 * (Parameters.xi : ℝ) - 2) * Real.log p ^ d)
      =o[atTop] (fun p : ℝ => p) := by
  have hb : (Parameters.beta : ℝ) < 1 := by
    exact_mod_cast Parameters.guard_exponents.1
  have hg : (Parameters.beta : ℝ) + 2 * (Parameters.xi : ℝ) - 2 < 1 := by
    exact_mod_cast Parameters.guard_exponents.2.2
  simpa only [Real.rpow_one] using
    (absorb_polylog _ 1 d hb).add (absorb_polylog _ 1 d hg)

end WholeMachine.Costs
