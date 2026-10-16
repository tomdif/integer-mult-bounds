import Target
import Mathlib.Analysis.Normed.Group.Constructions

/-! Checked counterexamples to invalid numerical and visited-space shortcuts. -/
namespace WholeMachine.Counterexamples

noncomputable def D (v : ℝ × ℝ) : ℝ × ℝ := (8 * v.1, v.2 / 8)
noncomputable def H (v : ℝ × ℝ) : ℝ × ℝ := ((v.1 + v.2) / 2, (v.1 - v.2) / 2)
noncomputable def restore (v : ℝ × ℝ) : ℝ × ℝ := (v.1 / 4, 16 * v.2)

theorem completed_identity (v : ℝ × ℝ) : restore (H (H (D v))) = v := by
  apply Prod.ext <;> dsimp [restore, H, D] <;> ring

theorem first_call_out_of_domain : 1 < ‖D ((1 / 2 : ℝ), 0)‖ := by
  norm_num [D, Prod.norm_def]

open Target

/-- Write, visit a second cell, return, erase, halt. -/
def eraser : Program 0 4 0 where
  initial := 0
  table := fun q tape =>
    if q = 0 then some (1, fun i => if i = 0 then (2, .right) else (tape i, .stay))
    else if q = 1 then some (2, fun i => if i = 0 then (0, .left) else (tape i, .stay))
    else if q = 2 then some (3, fun i => if i = 0 then (0, .stay) else (tape i, .stay))
    else none

def emptyInput : Configuration 0 4 0 := input eraser [] []

theorem eraser_halts : halted eraser (run eraser emptyInput 3) := by
  unfold halted
  decide

theorem eraser_visited : (visited eraser emptyInput 3).card = 4 := by decide

theorem eraser_final_blank (i : Fin 3) (j : ℤ) :
    (run eraser emptyInput 3).cells i j = 0 := by
  fin_cases i <;>
    simp [run, step, eraser, emptyInput, input, word, scanned, Motion.displacement] <;> tauto

end WholeMachine.Counterexamples
