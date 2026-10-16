import BoundedCalls
import Recovery

/-! Numerical assembly of the CRT/Fourier/product/inverse-CRT pipeline.
The actual tape implementations and the exact Fourier/convolution identity
are deliberately explicit hypotheses, not axioms or a completed theorem.
-/
namespace WholeMachine.RecoveryPipeline

variable {V : Type*} [NormedCommRing V] [NormedSpace ℝ V]

def Contract (A : V →L[ℝ] V) (f : V → V) (e : ℝ) : Prop :=
  ∀ v : V, ‖v‖ ≤ 1 → ‖f v - A v‖ ≤ e

def Contraction (A : V →L[ℝ] V) : Prop := ∀ v : V, ‖A v‖ ≤ ‖v‖

theorem apply_error (A : V →L[ℝ] V) (f : V → V) (e : ℝ)
    (hA : Contraction A) (hf : Contract A f e) (u v : V) (hu : ‖u‖ ≤ 1) :
    ‖f u - A v‖ ≤ e + ‖u - v‖ := by
  have hid : f u - A v = (f u - A u) + A (u - v) := by rw [map_sub]; abel
  rw [hid]
  exact (norm_add_le _ _).trans (add_le_add (hf u hu) (hA (u - v)))

omit [NormedSpace ℝ V] in
theorem norm_from_error (u v : V) (r b : ℝ) (he : ‖u - v‖ ≤ r) (hv : ‖v‖ ≤ b) :
    ‖u‖ ≤ r + b := (norm_le_norm_sub_add u v).trans (add_le_add he hv)

theorem forward (C F : V →L[ℝ] V) (c f : V → V) (e : ℝ)
    (_he : 0 ≤ e) (he' : e ≤ 1 / 200)
    (hC : Contraction C) (hF : Contraction F)
    (hc : Contract C c e) (hf : Contract F f e)
    (x : V) (hx : ‖x‖ ≤ 1 / 4) :
    ‖f (c x) - F (C x)‖ ≤ 2 * e ∧ ‖f (c x)‖ ≤ 13 / 50 := by
  have hcx := hc x (by linarith)
  have hcn := norm_from_error _ _ _ _ hcx ((hC x).trans hx)
  have herr := (apply_error F f e hF hf (c x) (C x) (by linarith)).trans
    (add_le_add le_rfl hcx)
  have hh : ‖f (c x) - F (C x)‖ ≤ 2 * e := by linarith
  have hn := norm_from_error _ _ _ _ hh ((hF (C x)).trans ((hC x).trans hx))
  exact ⟨hh, by linarith⟩

omit [NormedSpace ℝ V] in
theorem product_error (P : V → V → V) (e : ℝ) (he : 0 ≤ e)
    (hP : ∀ u v : V, ‖u‖ ≤ 1 → ‖v‖ ≤ 1 → ‖P u v - u * v‖ ≤ e)
    (u v a b : V) (hu : ‖u‖ ≤ 13 / 50) (hv : ‖v‖ ≤ 13 / 50)
    (ha : ‖a‖ ≤ 1 / 4) (heu : ‖u - a‖ ≤ 2 * e) (hev : ‖v - b‖ ≤ 2 * e) :
    ‖P u v - a * b‖ ≤ 3 * e := by
  have hid : P u v - a * b = (P u v - u * v) + ((u - a) * v + a * (v - b)) := by ring
  rw [hid]
  calc
    _ ≤ ‖P u v - u * v‖ + (‖(u - a) * v‖ + ‖a * (v - b)‖) :=
      (norm_add_le _ _).trans (add_le_add le_rfl (norm_add_le _ _))
    _ ≤ e + (‖u - a‖ * ‖v‖ + ‖a‖ * ‖v - b‖) :=
      add_le_add (hP u v (by linarith) (by linarith))
        (add_le_add (norm_mul_le _ _) (norm_mul_le _ _))
    _ ≤ e + ((2 * e) * (13 / 50) + (1 / 4) * (2 * e)) := by gcongr
    _ ≤ 3 * e := by linarith

/-- Every nonlinear pipeline call has its bounded-input premise established.
The scaled-convolution bound is the remaining exact transform identity seam. -/
theorem pipeline (C F G I : V →L[ℝ] V) (c f g inv : V → V) (P : V → V → V)
    (e S : ℝ) (he : 0 ≤ e) (he' : e ≤ 1 / 200) (hS : 0 ≤ S) (hSe : S * e ≤ 1 / 64)
    (hC : Contraction C) (hF : Contraction F) (hG : Contraction G) (hI : Contraction I)
    (hc : Contract C c e) (hf : Contract F f e) (hg : Contract G g e) (hi : Contract I inv e)
    (hP : ∀ u v : V, ‖u‖ ≤ 1 → ‖v‖ ≤ 1 → ‖P u v - u * v‖ ≤ e)
    (x y : V) (hx : ‖x‖ ≤ 1 / 4) (hy : ‖y‖ ≤ 1 / 4)
    (hscaled : ‖S • G (F (C x) * F (C y))‖ ≤ 1 / 16) :
    ‖inv (S • g (P (f (c x)) (f (c y)))) - I (S • G (F (C x) * F (C y)))‖ ≤
      (4 * S + 1) * e := by
  have hfx := forward C F c f e he he' hC hF hc hf x hx
  have hfy := forward C F c f e he he' hC hF hc hf y hy
  have hax : ‖F (C x)‖ ≤ 1 / 4 := (hF _).trans ((hC _).trans hx)
  have hay : ‖F (C y)‖ ≤ 1 / 4 := (hF _).trans ((hC _).trans hy)
  have hprod := product_error P e he hP _ _ _ _ hfx.2 hfy.2 hax hfx.1 hfy.1
  have hpideal : ‖F (C x) * F (C y)‖ ≤ 1 / 16 := by
    calc
      _ ≤ ‖F (C x)‖ * ‖F (C y)‖ := norm_mul_le _ _
      _ ≤ (1 / 4 : ℝ) * (1 / 4) := by gcongr
      _ = _ := by norm_num
  have hpactual := norm_from_error _ _ _ _ hprod hpideal
  have hfourier : ‖g (P (f (c x)) (f (c y))) - G (F (C x) * F (C y))‖ ≤ 4 * e := by
    have hh := apply_error G g e hG hg (P (f (c x)) (f (c y)))
      (F (C x) * F (C y)) (by linarith)
    linarith
  have hscale : ‖S • g (P (f (c x)) (f (c y))) - S • G (F (C x) * F (C y))‖ ≤ 4 * S * e := by
    rw [← smul_sub, norm_smul, Real.norm_eq_abs, abs_of_nonneg hS]
    calc
      _ ≤ S * (4 * e) := mul_le_mul_of_nonneg_left hfourier hS
      _ = _ := by ring
  have hinput := norm_from_error _ _ _ _ hscale hscaled
  have hfinish := apply_error I inv e hI hi (S • g (P (f (c x)) (f (c y))))
    (S • G (F (C x) * F (C y))) (by nlinarith)
  nlinarith

/-- Any norm-one real output coordinate with the exact integer identity can
now use the predecessor's checked nearest-integer recovery theorem. -/
theorem recover_coordinate (B S e : ℝ) (actual ideal : V) (coord : V →L[ℝ] ℝ) (m : ℤ)
    (hcoord : ∀ v : V, |coord v| ≤ ‖v‖)
    (hB : 4 ≤ B) (hS : 0 ≤ S) (hSB : S ≤ B) (he : 0 ≤ e)
    (hprecision : e * B^10 ≤ 1)
    (herror : ‖actual - ideal‖ ≤ (4*S+1)*e)
    (hexact : 16 * B^2 * S * coord ideal = (m : ℝ)) :
    round (16 * B^2 * S * coord actual) = m := by
  apply OuterRecovery.exactRecovery B S e _ m hB hS hSB he hprecision
  rw [← hexact, ← mul_sub, ← map_sub, abs_mul, abs_of_nonneg (by positivity)]
  calc
    _ ≤ (16 * B^2 * S) * ((4*S+1)*e) :=
      mul_le_mul_of_nonneg_left ((hcoord _).trans herror) (by positivity)
    _ = _ := by ring

end WholeMachine.RecoveryPipeline
