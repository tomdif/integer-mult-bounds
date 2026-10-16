import Mathlib.Tactic

/-! Exact parameters of multiplication-proof-completion/PROOF.md. These are
arithmetic facts, not a time bound for a program. -/
namespace WholeMachine.Parameters

def C : ℚ := 1722052684227397319529 / 10^24
def kappa : ℚ := C - 1 / 10^46 - 1 / 10^70
def delta : ℚ := (1025 / 1024) / 10^104
def epsilon : ℚ := 1 - delta
def beta : ℚ := 1 - 3 * delta
def q : ℚ := C - 2 / 10^104
def aEff : ℚ := C - (3 / 2) / 10^104
def xi : ℚ := epsilon * (1 + q) - 3 / 32 + 1 / 10^104
def aBit : ℚ := (173 / 100000) * (1 - 173 / 100000)

theorem parameter_order :
    0 < kappa ∧ kappa < q ∧ q < aEff ∧ aEff < aBit ∧
    0 < beta ∧ beta < epsilon ∧ epsilon < 1 ∧
    1 / 2 < xi ∧ xi < epsilon := by
  norm_num [C, kappa, delta, epsilon, beta, q, aEff, xi, aBit]

theorem guard_exponents : beta < 1 ∧ beta + 2 * (1 - epsilon) < 1 ∧
    beta + 2 * xi - 2 < 1 := by
  norm_num [C, delta, epsilon, beta, q, xi]

inductive CostRow where
  | synthetic | fullRoute | dense | groupRoute | groupScan
  | boundary | sparse | shortProduct | face
  deriving DecidableEq, Fintype

def costPower : CostRow → ℚ
  | .synthetic => 1 - epsilon * q
  | .fullRoute => 1 - aEff
  | .dense => epsilon - q * beta
  | .groupRoute => epsilon - aEff * beta
  | .groupScan => epsilon - beta
  | .boundary => epsilon - xi + 29 / 32
  | .sparse => epsilon + 1 / 2 - xi
  | .shortProduct => 1 - epsilon
  | .face => epsilon + beta - 30

theorem all_cost_powers_lt (row : CostRow) : costPower row < 1 - kappa := by
  cases row <;>
    norm_num [costPower, C, kappa, delta, epsilon, beta, q, aEff, xi]

theorem explicit_uniform_slack (row : CostRow) :
    costPower row + 1 / 10^47 < 1 - kappa := by
  cases row <;>
    norm_num [costPower, C, kappa, delta, epsilon, beta, q, aEff, xi]

end WholeMachine.Parameters
