import Mathlib.Tactic

/-! Quantified arithmetic used by the source-bound recursive refit proof.
The event audit supplies the premises; no machine semantics are postulated
as axioms or claimed to follow from these arithmetic lemmas. -/

namespace RefitRecursion

theorem properChild (e : ℕ) (he : 73 ≤ e) : 48 * (e / 73) < e := by
  omega

theorem deferredReservation (h : ℕ) (hh : 512 ≤ h) :
    16 * ((h + 63) / 64 + (h + 127) / 128 + 11) ≤ h := by
  omega

theorem rowCapacity (bits depth G q : ℕ) (hG : 0 < G)
    (hq : q = (bits * depth + 128 * G - 1) / (128 * G)) :
    bits * depth ≤ q * (128 * G) := by
  have hK : 0 < 128 * G := by omega
  have hmod := Nat.mod_lt (bits * depth + 128 * G - 1) hK
  have hdiv := Nat.mod_add_div (bits * depth + 128 * G - 1) (128 * G)
  subst q
  calc
    bits * depth ≤ (128 * G) * ((bits * depth + 128 * G - 1) / (128 * G)) := by omega
    _ = ((bits * depth + 128 * G - 1) / (128 * G)) * (128 * G) := Nat.mul_comm _ _

theorem elevenRows (ell depth : ℕ) (hd : depth ≤ 2 * ell) :
    (2644 * depth + 128 * (4 * ell + 6) - 1) / (128 * (4 * ell + 6)) ≤ 11 := by
  have hK : 0 < 128 * (4 * ell + 6) := by omega
  apply (Nat.div_le_iff_le_mul hK).2
  omega

theorem heightBound (A : ℕ → ℕ) (s E : ℕ) (hB : 4 ≤ s + E)
    (leaf : ∀ e, e < 73 → A e ≤ 8 * e)
    (step : ∀ e, 73 ≤ e → A e ≤ A (48 * (e / 73)) + s * (e / 73) + E) :
    ∀ e, A e ≤ 2 * (s + E) * e := by
  intro e
  induction e using Nat.strong_induction_on with
  | h e ih =>
    by_cases he : e < 73
    · have hl := leaf e he
      nlinarith
    · have he' : 73 ≤ e := by omega
      have hi := ih (48 * (e / 73)) (properChild e he')
      have hs := step e he'
      have hf : 1 ≤ e / 73 := by omega
      have hdiv : 73 * (e / 73) ≤ e := by omega
      have hm := Nat.mul_le_mul_left (2 * (s + E)) hdiv
      have hE := Nat.mul_le_mul_left E hf
      nlinarith

theorem deferredHeight (B finished active total : ℕ) (hB : 1 ≤ B)
    (hs : finished + active ≤ total) :
    finished + 2 * B * active + 18 * total ≤ (2 * B + 18) * total := by
  have hm := Nat.mul_le_mul_left (2 * B) hs
  nlinarith

#print axioms properChild
#print axioms deferredReservation
#print axioms rowCapacity
#print axioms elevenRows
#print axioms heightBound
#print axioms deferredHeight

end RefitRecursion
