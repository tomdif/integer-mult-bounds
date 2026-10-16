/-
Apache-2.0. Thomas DiFiore with OpenAI Codex assistance.
The common-label semantics and conjugation proof are DreamingOfClouds's
unchanged LemmaG.Stream. This file proves a conditional replacement rule
and the commuting-add identity used by our four terminal refits.
It does not instantiate native recipes or prove a machine time bound.
-/
import LemmaG.Stream

namespace TerminalRefit
open LemmaG

variable {ι Λ K M : Type*} [DecidableEq ι] [Semiring K]
  [AddCommMonoid M] [Module K M]

/-- Two additions into one destination commute when neither reads it. -/
theorem adds_commute (d s t : ι) (hs : s ≠ d) (ht : t ≠ d)
    (a b : K) (x : ι → M) :
    (Event.add d t b : Event ι Λ K).scal ((Event.add d s a : Event ι Λ K).scal x) =
    (Event.add d s a : Event ι Λ K).scal ((Event.add d t b : Event ι Λ K).scal x) := by
  funext i
  by_cases hi : i = d
  · subst i
    simp [Event.scal, Event.phys, hs, ht, add_assoc, add_comm, add_left_comm]
  · simp [Event.scal, Event.phys, hi]

/-- A preceding sign or any other scaling stays before the commuting pair. -/
theorem scale_then_adds_commute (d s t : ι) (hs : s ≠ d) (ht : t ≠ d)
    (a b c : K) (x : ι → M) :
    (Event.add d t b : Event ι Λ K).scal
      ((Event.add d s a : Event ι Λ K).scal ((Event.scale d c : Event ι Λ K).scal x)) =
    (Event.add d s a : Event ι Λ K).scal
      ((Event.add d t b : Event ι Λ K).scal ((Event.scale d c : Event ι Λ K).scal x)) :=
  adds_commute d s t hs ht a b ((Event.scale d c : Event ι Λ K).scal x)

/-- Label schedules may differ internally. Identical scalar action and final
labels imply identical physical action on arbitrary, possibly correlated inputs,
provided both schedules are well-labelled and all their transports are exact. -/
theorem replace_program (T : Λ → M ≃ₗ[K] M)
    (rec₁ rec₂ : Λ → Λ → M → M) (old new : List (Event ι Λ K))
    (initial : ι → Λ)
    (hrec₁ : Stream.RecipesExact T rec₁ old)
    (hrec₂ : Stream.RecipesExact T rec₂ new)
    (hlabel₁ : Stream.WellLabelled old initial)
    (hlabel₂ : Stream.WellLabelled new initial)
    (hend : Stream.labRun old initial = Stream.labRun new initial)
    (hshadow : ∀ x : ι → M, Stream.scalRun old x = Stream.scalRun new x)
    (h : ι → M) :
    Stream.physRun rec₁ old h = Stream.physRun rec₂ new h := by
  have ho := Stream.conj T rec₁ old initial (Stream.Dinv T initial h) hrec₁ hlabel₁
  have hn := Stream.conj T rec₂ new initial (Stream.Dinv T initial h) hrec₂ hlabel₂
  rw [Stream.D_Dinv] at ho hn
  rw [ho, hn, hend, hshadow]

end TerminalRefit

#print axioms TerminalRefit.adds_commute
#print axioms TerminalRefit.scale_then_adds_commute
#print axioms TerminalRefit.replace_program
