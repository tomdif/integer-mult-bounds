import BoundedCalls
import Intervals
import Asymptotics
import Composition
import RecoveryPipeline
import ProofCounterexamples
import Lean.Util.CollectAxioms

/-! This audit deliberately does not assert `WholeMachine.Target.Complete`.
It checks every declaration in the new namespace and the imported recovery
module, including generated auxiliary declarations. Standard axioms only.
Successful checking remains scoped progress, not whole-machine completion. -/

open Lean in
run_cmd do
  let env ← getEnv
  let mut count : Nat := 0
  let mut theoremCount : Nat := 0
  for (name, ci) in env.constants.toList do
    if (`WholeMachine).isPrefixOf name || (`OuterRecovery).isPrefixOf name ||
        name.toString.startsWith "_private.BoundedCalls." ||
        name.toString.startsWith "_private.Intervals." ||
        name.toString.startsWith "_private.Asymptotics." ||
        name.toString.startsWith "_private.Composition." ||
        name.toString.startsWith "_private.RecoveryPipeline." ||
        name.toString.startsWith "_private.ProofCounterexamples." ||
        name.toString.startsWith "_private.Target." ||
        name.toString.startsWith "_private.Parameters." ||
        name.toString.startsWith "_private.Recovery." then
      for ax in ← collectAxioms name do
        unless #[``propext, ``Classical.choice, ``Quot.sound].contains ax do
          throwError "{name} depends on unapproved axiom {ax}"
      count := count + 1
      if ci.isTheorem then theoremCount := theoremCount + 1
  logInfo m!"SCOPED_AXIOM_AUDIT declarations={count} theorems={theoremCount}"

#print axioms WholeMachine.BoundedCalls.scaled_schedule
#print axioms WholeMachine.Intervals.horner_interval
#print axioms WholeMachine.Costs.cost_row_absorbed
#print axioms WholeMachine.Composition.run_sequence
#print axioms WholeMachine.Composition.visited_sequence
#print axioms WholeMachine.Composition.compose_halting_runs
#print axioms WholeMachine.RecoveryPipeline.pipeline
#print axioms WholeMachine.RecoveryPipeline.recover_coordinate
#print axioms WholeMachine.Counterexamples.eraser_visited
#check WholeMachine.Target.Complete
