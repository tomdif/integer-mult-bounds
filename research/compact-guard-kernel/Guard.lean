import Mathlib.Tactic

/-! Dirty compact controls and exceptional-address repair.
The actual word is credited to the retained Colkitt / PR1673 construction.
This file proves arithmetic and permutation implications, not tape costs.
Apache-2.0. Thomas DiFiore with substantial OpenAI Codex assistance. -/
namespace CompactGuard

/-- An exact modular version of the four updates in one F word.
The source bit z is read-only. The returned coordinates are (t, y). -/
def flip (B R z t y : ℤ) : ℤ × ℤ :=
  let y₁ := (y + 2*z*t) % R
  let t₁ := (t + y₁ % 2) % B
  let y₂ := (y₁ + z*(1 - 2*t₁)) % R
  let t₂ := (t₁ - ((y₂ % 2 + z) % 2)) % B
  (t₂, y₂)

/-- The scratch increment fits, and neither y addition crosses a guard.
No bound on a compact control digit is needed here: only its bit z is read. -/
theorem guardBounds (B M h t e z : ℤ)
    (hB : 2 ≤ B) (hh₀ : 2*B ≤ h) (hh₁ : h < M - 2*B)
    (ht₀ : 0 ≤ t) (ht₁ : t ≤ B-2)
    (he₀ : 0 ≤ e) (he₁ : e ≤ 1) (hz₀ : 0 ≤ z) (hz₁ : z ≤ 1) :
    (0 ≤ 2*h+e+2*z*t ∧ 2*h+e+2*z*t < 2*M) ∧
    (0 ≤ t+e ∧ t+e < B) ∧
    (0 ≤ 2*h+e+z*(1-2*e) ∧ 2*h+e+z*(1-2*e) < 2*M) := by
  interval_cases e <;> interval_cases z <;> simp_all <;> omega

/-- Exact F endpoint, including modular wrap semantics on arbitrary bad inputs. -/
theorem flipCorrect (B M h t e z : ℤ)
    (hB : 2 ≤ B) (hh₀ : 2*B ≤ h) (hh₁ : h < M - 2*B)
    (ht₀ : 0 ≤ t) (ht₁ : t ≤ B-2)
    (he₀ : 0 ≤ e) (he₁ : e ≤ 1) (hz₀ : 0 ≤ z) (hz₁ : z ≤ 1) :
    flip B (2*M) z t (2*h+e) = (t, 2*h+(e+z)%2) := by
  have bounds := guardBounds B M h t e z hB hh₀ hh₁ ht₀ ht₁ he₀ he₁ hz₀ hz₁
  have hp : (2*h+e+2*z*t)%2 = e := by
    interval_cases e <;> interval_cases z <;> omega
  have hid : 2*h+e+2*z*t+z*(1-2*(t+e)) = 2*h+e+z*(1-2*e) := by ring
  have heq : 2*h+e+z*(1-2*e) = 2*h+(e+z)%2 := by
    interval_cases e <;> interval_cases z <;> norm_num
  have hrecover : ((2*h+(e+z)%2)%2+z)%2 = e := by
    interval_cases e <;> interval_cases z <;> omega
  dsimp only [flip]
  rw [Int.emod_eq_of_lt bounds.1.1 bounds.1.2, hp,
      Int.emod_eq_of_lt bounds.2.1.1 bounds.2.1.2, hid,
      Int.emod_eq_of_lt bounds.2.2.1 bounds.2.2.2, heq, hrecover]
  have htB : t < B := by omega
  simp [Int.emod_eq_of_lt ht₀ htB]

/-- Loading a source bit may reach B-1, but never carries to the next digit. -/
theorem loadedControl (B u x : ℤ) (_hB : 2 ≤ B)
    (hu₀ : 0 ≤ u) (hu₁ : u ≤ B-2) (hx₀ : 0 ≤ x) (hx₁ : x ≤ 1) :
    (0 ≤ u+x ∧ u+x < B) ∧ (u+x)%B = u+x ∧ (u+x)-x = u := by
  have hlo : 0 ≤ u+x := by omega
  have hhi : u+x < B := by omega
  exact ⟨⟨hlo,hhi⟩, Int.emod_eq_of_lt hlo hhi, by ring⟩

/-- The two compact parities differ by exactly the loaded source bit. -/
theorem parityCancellation (e u x : ℤ) :
    ((e+u%2)%2+(u+x)%2)%2 = (e+x)%2 := by omega

/-- Two F calls with an intervening source load implement the desired XOR.
Both calls restore t; h is unchanged, including source bits inside guards. -/
theorem pairedFlipCorrect (B M h t e u x : ℤ)
    (hB : 2 ≤ B) (hh₀ : 2*B ≤ h) (hh₁ : h < M-2*B)
    (ht₀ : 0 ≤ t) (ht₁ : t ≤ B-2)
    (he₀ : 0 ≤ e) (he₁ : e ≤ 1) :
    let first := flip B (2*M) (u%2) t (2*h+e)
    flip B (2*M) ((u+x)%2) first.1 first.2 = (t,2*h+(e+x)%2) := by
  have hu₀ : 0 ≤ u%2 := Int.emod_nonneg _ (by norm_num)
  have hu₁ : u%2 ≤ 1 := by omega
  have hx₀ : 0 ≤ (u+x)%2 := Int.emod_nonneg _ (by norm_num)
  have hx₁ : (u+x)%2 ≤ 1 := by omega
  have he'₀ : 0 ≤ (e+u%2)%2 := Int.emod_nonneg _ (by norm_num)
  have he'₁ : (e+u%2)%2 ≤ 1 := by omega
  dsimp only
  rw [flipCorrect B M h t e (u%2) hB hh₀ hh₁ ht₀ ht₁ he₀ he₁ hu₀ hu₁]
  dsimp only
  rw [flipCorrect B M h t ((e+u%2)%2) ((u+x)%2)
      hB hh₀ hh₁ ht₀ ht₁ he'₀ he'₁ hx₀ hx₁, parityCancellation]

/-- Swap front/back, add to the back, swap back. Arbitrary dirty back survives. -/
theorem shuttle {G : Type*} [Add G] (u b c : G) :
    let swapped := (b,u)
    let added := (swapped.1,swapped.2+c)
    (added.2,added.1) = (u+c,b) := rfl

/-- A source may read any higher guard bit or untouched outside bit, even in
another active guard. Completed target flips leave every such source fixed. -/
theorem sourcePreserved {ι O A : Type*} (high low : ι → ℤ) (outside : O)
    (source : (ι → ℤ) → O → A)
    (hlo : ∀ i, 0 ≤ low i) (hhi : ∀ i, low i ≤ 1) :
    source (fun i => (2*high i+low i)/2) outside = source high outside := by
  have heq : (fun i => (2*high i+low i)/2) = high := by
    funext i
    have h₀ := hlo i
    have h₁ := hhi i
    omega
  rw [heq]

/-- Signed component updates commute with packing. This applies to arbitrary
uneven guard weights and an arbitrary untouched outside contribution. -/
theorem packedUpdates {ι : Type*} [Fintype ι]
    (outside : ℤ) (weight digit delta : ι → ℤ) :
    (outside + ∑ i, weight i * digit i) + ∑ i, weight i * delta i =
      outside + ∑ i, weight i * (digit i + delta i) := by
  simp [mul_add, Finset.sum_add_distrib, add_assoc]

/-- Mixed-radix words have a genuine bounded integer representation. Radices
may vary, so untouched gaps and dirty inactive high digits can be included. -/
def pack : List (ℤ × ℤ) → ℤ
  | [] => 0
  | (radix,digit) :: rest => digit + radix * pack rest

def capacity : List (ℤ × ℤ) → ℤ
  | [] => 1
  | (radix,_) :: rest => radix * capacity rest

def Valid : List (ℤ × ℤ) → Prop
  | [] => True
  | (radix,digit) :: rest => 0 < radix ∧ 0 ≤ digit ∧ digit < radix ∧ Valid rest

theorem packBounds (cells : List (ℤ × ℤ)) (valid : Valid cells) :
    0 < capacity cells ∧ 0 ≤ pack cells ∧ pack cells < capacity cells := by
  induction cells with
  | nil => norm_num [capacity,pack]
  | cons cell rest ih =>
    rcases cell with ⟨r,d⟩
    rcases valid with ⟨hr,hd₀,hd₁,hrest⟩
    rcases ih hrest with ⟨hc,hp₀,hp₁⟩
    dsimp [capacity,pack]
    refine ⟨mul_pos hr hc, ?_, ?_⟩
    · exact add_nonneg hd₀ (mul_nonneg (le_of_lt hr) hp₀)
    · have hg : pack rest + 1 ≤ capacity rest := by omega
      have hm := mul_le_mul_of_nonneg_left hg (le_of_lt hr)
      nlinarith

/-- A packed update whose resulting digits remain valid cannot wrap the
whole field. This justifies replacing modular rotations by signed arithmetic. -/
theorem packedNoWrap (cells : List (ℤ × ℤ)) (valid : Valid cells) :
    pack cells % capacity cells = pack cells := by
  exact Int.emod_eq_of_lt (packBounds cells valid).2.1 (packBounds cells valid).2.2

/-- The exact independent single-guard count has the advertised union bound. -/
theorem singleGuardDensity (B M : ℝ) (hB : 1 ≤ B) (hM : 4*B ≤ M) :
    1 - ((B-1)/B)^2 * ((M-4*B)/M) ≤ 2/B + 4*B/M := by
  have hBp : 0 < B := by linarith
  have hMp : 0 < M := by linarith
  have hx : 0 ≤ 1/B := by positivity
  have hy : 0 ≤ 4*B/M := by positivity
  have hy' : 4*B/M ≤ 1 := (div_le_one hMp).mpr hM
  have eq₁ : (B-1)/B = 1-1/B := by field_simp
  have eq₂ : (M-4*B)/M = 1-4*B/M := by field_simp
  rw [eq₁,eq₂]
  have h₁ := mul_nonneg (sq_nonneg (1/B)) (sub_nonneg.mpr hy')
  have h₂ := mul_nonneg hx hy
  have htwo : 2/B = 2*(1/B) := by ring
  rw [htwo]
  nlinarith

/-- Tensoring independent guards loses at most r times the single failure
fraction. No independence of the selected source bits is required. -/
theorem productFailure (a : ℝ) (ha₀ : 0 ≤ a) (ha₁ : a ≤ 1) (r : ℕ) :
    1-a^r ≤ (r:ℝ)*(1-a) := by
  induction r with
  | zero => simp
  | succ r ih =>
    have hmul := mul_le_mul_of_nonneg_left ih ha₀
    have hnonneg : 0 ≤ (r:ℝ)*(1-a) := by positivity
    have hcap := mul_le_of_le_one_left hnonneg ha₁
    rw [pow_succ]
    push_cast
    nlinarith

/-- Complete exact-count-to-union-bound implication for any number of guards. -/
theorem allGuardDensity (B M : ℝ) (hB : 1 ≤ B) (hM : 4*B ≤ M) (r : ℕ) :
    1 - (((B-1)/B)^2 * ((M-4*B)/M))^r ≤ (r:ℝ)*(2/B+4*B/M) := by
  have hBp : 0 < B := by linarith
  have hMp : 0 < M := by linarith
  have hx₀ : 0 ≤ (B-1)/B := div_nonneg (by linarith) (le_of_lt hBp)
  have hx₁ : (B-1)/B ≤ 1 := (div_le_one hBp).mpr (by linarith)
  have hy₀ : 0 ≤ (M-4*B)/M := div_nonneg (by linarith) (le_of_lt hMp)
  have hy₁ : (M-4*B)/M ≤ 1 := (div_le_one hMp).mpr (by linarith)
  have hs : ((B-1)/B)^2 ≤ 1 := by nlinarith
  have ha₀ : 0 ≤ ((B-1)/B)^2 * ((M-4*B)/M) := mul_nonneg (sq_nonneg _) hy₀
  have ha₁ : ((B-1)/B)^2 * ((M-4*B)/M) ≤ 1 := by
    calc
      ((B-1)/B)^2 * ((M-4*B)/M) ≤ 1 * ((M-4*B)/M) :=
        mul_le_mul_of_nonneg_right hs hy₀
      _ = (M-4*B)/M := one_mul _
      _ ≤ 1 := hy₁
  exact (productFailure _ ha₀ ha₁ r).trans
    (mul_le_mul_of_nonneg_left (singleGuardDensity B M hB hM) (Nat.cast_nonneg r))

/-- With the actual reservoir sizes the sorting payload is at most
3/(64 p^3) of the complete stream; keys cost another factor O(p). -/
theorem exceptionalDensity (p B M r : ℝ) (hp : 1 ≤ p)
    (hB : 64*p^4 ≤ B) (hM : 4*B^2 ≤ M)
    (hr₀ : 0 ≤ r) (hr₁ : r ≤ p) :
    r*(2/B+4*B/M) ≤ 3/(64*p^3) := by
  have hpp : 0 < p := by linarith
  have hp4 : 0 < p^4 := by positivity
  have hBp : 0 < B := by nlinarith
  have hMp : 0 < M := by nlinarith [sq_pos_of_pos hBp]
  have hsmall : 4*B/M ≤ 1/B := by
    apply (div_le_div_iff₀ hMp hBp).mpr
    nlinarith
  calc
    r*(2/B+4*B/M) ≤ r*(2/B+1/B) :=
      mul_le_mul_of_nonneg_left (by linarith) hr₀
    _ = r*(3/B) := by ring
    _ ≤ p*(3/B) := mul_le_mul_of_nonneg_right hr₁ (by positivity)
    _ ≤ p*(3/(64*p^4)) := by
      apply mul_le_mul_of_nonneg_left _ (le_of_lt hpp)
      exact div_le_div_of_nonneg_left (by norm_num) (by positivity) hB
    _ = 3/(64*p^3) := by field_simp

/-- A fibrewise controlled rotation is a permutation on every address,
including addresses outside the guarded set. -/
def controlledAdd {A G : Type*} [AddGroup G] (offset : A → G) : (A × G) ≃ (A × G) where
  toFun x := (x.1, x.2 + offset x.1)
  invFun x := (x.1, x.2 - offset x.1)
  left_inv x := by simp
  right_inv x := by simp

/-- If two permutations agree on an invariant good set, the raw one also
preserves that set. Invariance is derived, not separately assumed for S. -/
theorem rawPreservesGood {A : Type*} (S T : A ≃ A) (good : A → Prop)
    (hT : ∀ x, good (T x) ↔ good x)
    (agree : ∀ x, good x → S x = T x) (x : A) :
    good (S x) ↔ good x := by
  constructor
  · intro hx
    have hy : good (T.symm (S x)) := by
      apply (hT (T.symm (S x))).mp
      simpa using hx
    have he : S (T.symm (S x)) = S x := by rw [agree _ hy]; simp
    have hi := S.injective he
    simpa [hi] using hy
  · intro hx
    rw [agree x hx]
    exact (hT x).mpr hx

/-- Postprocess current bad addresses only, using the inverse raw word. -/
noncomputable def repair {A : Type*} (S T : A ≃ A) (good : A → Prop) (z : A) : A := by
  classical
  exact if good z then z else T (S.symm z)

/-- The repair agrees globally with T ∘ S⁻¹, so bad keys cannot collide. -/
theorem repairEquals {A : Type*} (S T : A ≃ A) (good : A → Prop)
    (hT : ∀ x, good (T x) ↔ good x)
    (agree : ∀ x, good x → S x = T x) (z : A) :
    repair S T good z = T (S.symm z) := by
  classical
  by_cases hz : good z
  · have hx : good (S.symm z) := by
      apply (rawPreservesGood S T good hT agree (S.symm z)).mp
      simpa using hz
    have he := agree (S.symm z) hx
    simpa [repair, hz] using he
  · simp [repair, hz]

/-- Repaired payload destinations are the ideal destinations for every input. -/
theorem repairCorrect {A : Type*} (S T : A ≃ A) (good : A → Prop)
    (hT : ∀ x, good (T x) ↔ good x)
    (agree : ∀ x, good x → S x = T x) (x : A) :
    repair S T good (S x) = T x := by
  rw [repairEquals S T good hT agree]
  simp

/-- The current bad keys fill exactly the bad holes, with no duplicates. -/
theorem repairBijective {A : Type*} (S T : A ≃ A) (good : A → Prop)
    (hT : ∀ x, good (T x) ↔ good x)
    (agree : ∀ x, good x → S x = T x) :
    Function.Bijective (repair S T good) ∧
      ∀ z, good (repair S T good z) ↔ good z := by
  have hf : repair S T good = fun z => T (S.symm z) :=
    funext (repairEquals S T good hT agree)
  rw [hf]
  constructor
  · exact T.bijective.comp S.symm.bijective
  · intro z
    rw [hT]
    have hs := rawPreservesGood S T good hT agree (S.symm z)
    simpa using hs.symm

#print axioms guardBounds
#print axioms flipCorrect
#print axioms loadedControl
#print axioms parityCancellation
#print axioms pairedFlipCorrect
#print axioms shuttle
#print axioms sourcePreserved
#print axioms packedUpdates
#print axioms packBounds
#print axioms packedNoWrap
#print axioms singleGuardDensity
#print axioms productFailure
#print axioms allGuardDensity
#print axioms exceptionalDensity
#print axioms controlledAdd
#print axioms rawPreservesGood
#print axioms repairEquals
#print axioms repairCorrect
#print axioms repairBijective
end CompactGuard
