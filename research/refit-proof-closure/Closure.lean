import Mathlib.Tactic

/-! These are algebraic composition and weighted induction theorems.
No tape algorithm, FFT routine, or multiplication theorem is an axiom here. -/
namespace RefitClosure

theorem blockFactorization {L R : Type*} [AddGroup R]
    (left : L ≃ L) (right : R → R) (cross : L → R) (x : L) (y : R) :
    (left x, right y + cross (left.symm (left x))) =
      (left x, right y + cross x) := by simp

theorem conditionalShiftInverse {L R : Type*} [AddGroup R]
    (offset : L → R) (x : L) (y : R) :
    (x, (y + offset x) - offset x) = (x, y) := by simp

theorem normalizedSandwichScale (S z : ℂ) (hS : S ≠ 0) :
    S * (z / S) = z := by field_simp

theorem weightedClosure {I : Type*} [Fintype I]
    (T bound overhead : ℕ → ℝ) (child : ℕ → I → ℕ)
    (weight : ℕ → I → ℝ) (cutoff : ℕ)
    (weight_nonnegative : ∀ n i, 0 ≤ weight n i)
    (proper : ∀ n, cutoff ≤ n → ∀ i, child n i < n)
    (leaf : ∀ n, n < cutoff → T n ≤ bound n)
    (step : ∀ n, cutoff ≤ n →
      T n ≤ overhead n + ∑ i, weight n i * T (child n i))
    (supersolution : ∀ n, cutoff ≤ n →
      overhead n + ∑ i, weight n i * bound (child n i) ≤ bound n) :
    ∀ n, T n ≤ bound n := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    by_cases hn : n < cutoff
    · exact leaf n hn
    · have hn' : cutoff ≤ n := by omega
      calc
        T n ≤ overhead n + ∑ i, weight n i * T (child n i) := step n hn'
        _ ≤ overhead n + ∑ i, weight n i * bound (child n i) := by
          apply add_le_add (le_refl _)
          apply Finset.sum_le_sum
          intro i _
          exact mul_le_mul_of_nonneg_left (ih _ (proper n hn' i)) (weight_nonnegative n i)
        _ ≤ bound n := supersolution n hn'

theorem oldScanExceedsTarget :
    (1 : ℚ) - (1025 / 1024) / 10^104 >
      1 - (1722052684227397319529 / 10^24 - 1 / 10^46 - 1 / 10^70) := by
  norm_num

#print axioms blockFactorization
#print axioms conditionalShiftInverse
#print axioms normalizedSandwichScale
#print axioms weightedClosure
#print axioms oldScanExceedsTarget
end RefitClosure
