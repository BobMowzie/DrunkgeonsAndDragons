from abc import ABC

class Event(ABC):
	pass

class PhaseStartTurns(Event):
	pass

class PhaseModifyActions(Event):
	pass

class PhaseApplyEffects(Event):
	pass

class EventApplyEffect(Event):
	def __init__(self, caster, target, effect):
		self.caster = caster
		self.originalTarget = target
		self.target = target
		self.effect = effect

class PhasePreDamage(Event):
	pass

class PhaseDealDamage(Event):
	pass

class EventDealDamage(Event):
	def __init__(self, attacker, target, amount):
		self.attacker = attacker
		self.originalTarget = target
		self.target = target
		self.originalAmount = amount

class PhaseTakeDamage(Event):
	pass

class EventTakeDamage(Event):
	def __init__(self, attacker, target, amount):
		self.attacker = attacker
		self.originalTarget = target
		self.target = target
		self.originalAmount = amount

class PhasePostDamage(Event):
	pass

class PhaseEndTurns(Event):
	pass

class EventSubscription:
	def __init__(self, eventClass, function, order=0):
		self.eventClass = eventClass
		self.function = function
		self.order = order

class EventSubscriber(ABC):
	def __init__(self):
		self.subscribedEvents = []

	def subscribeEvent(self, eventClass, function, order=0):
		self.subscribedEvents.append(EventSubscription(eventClass, function, order))
