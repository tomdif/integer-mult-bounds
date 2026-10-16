import Mathlib.Tactic
import Mathlib.Algebra.Order.Round

/-! The numerical recovery implication only. No transform or machine theorem
is postulated here. Its approximation premise must come from TRANSFER.md. -/
namespace OuterRecovery

theorem productError (e : ℝ) (he : 0 ≤ e) :
    (2 * e) * (13 / 50) + (1 / 4) * (2 * e) + e ≤ 3 * e := by
  nlinarith

theorem scaleEnvelope (B S e : ℝ) (hB : 1 ≤ B) (hS : 0 ≤ S)
    (hSB : S ≤ B) (he : 0 ≤ e) :
    16 * B^2 * S * (4*S+1) * e ≤ 80 * B^4 * e := by
  have hb : 0 ≤ B := by linarith
  calc
    16 * B^2 * S * (4*S+1) * e
        ≤ 16 * B^2 * B * (5*B) * e := by gcongr <;> linarith
    _ = 80 * B^4 * e := by ring

theorem quarterRadius (B S e : ℝ) (hB : 4 ≤ B) (hS : 0 ≤ S)
    (hSB : S ≤ B) (he : 0 ≤ e) (hprecision : e * B^10 ≤ 1) :
    16 * B^2 * S * (4*S+1) * e < 1 / 4 := by
  have hb : 0 < B := by linarith
  have h6 : (4 : ℝ)^6 ≤ B^6 := by gcongr
  have hp : 0 < B^6 := by positivity
  calc
    16 * B^2 * S * (4*S+1) * e ≤ 80 * B^4 * e :=
      scaleEnvelope B S e (by linarith) hS hSB he
    _ ≤ 80 / B^6 := by
      apply (le_div_iff₀ hp).2
      have hid : 80 * B^4 * e * B^6 = 80 * (e * B^10) := by ring
      rw [hid]
      nlinarith
    _ ≤ 80 / (4 : ℝ)^6 := by gcongr
    _ < 1 / 4 := by norm_num

theorem roundOfQuarter (x : ℝ) (m : ℤ) (h : |x - (m : ℝ)| < 1 / 4) :
    round x = m := by
  rw [round_eq_iff]
  have hh := abs_lt.mp h
  constructor <;> linarith

theorem exactRecovery (B S e x : ℝ) (m : ℤ)
    (hB : 4 ≤ B) (hS : 0 ≤ S) (hSB : S ≤ B) (he : 0 ≤ e)
    (hprecision : e * B^10 ≤ 1)
    (herror : |x - (m : ℝ)| ≤ 16 * B^2 * S * (4*S+1) * e) :
    round x = m := by
  apply roundOfQuarter
  exact lt_of_le_of_lt herror (quarterRadius B S e hB hS hSB he hprecision)

#print axioms productError
#print axioms scaleEnvelope
#print axioms quarterRadius
#print axioms roundOfQuarter
#print axioms exactRecovery
end OuterRecovery
