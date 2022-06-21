from abc import ABC
import copy

class Event(ABC):
	def __init__(self, game):
		self.game = game
		self.newCanceled = False
		self.canceled = False

	def beginEvent(self):
		pass

	"""
	Called in between executing the subscription for different subscriber types.
	For example, after applying all clerics' divine barriers but before applying all paladins' shields, this function
	will get called to update the damage instances.
	"""
	def betweenSubscriberTypes(self):
		self.canceled = self.newCanceled

	def endEvent(self):
		pass

class PhaseStartTurns(Event):
	pass

class PhaseModifyActions(Event):
	pass

class PhaseApplyEffects(Event):
	pass

class EventApplyEffect(Event):
	def __init__(self, effect, game):
		super().__init__(game)
		self.caster = effect.caster
		self.target = effect.target
		self.effect = effect

class PhasePreDamage(Event):
	pass

class PhaseDealDamage(Event):
	pass

class EventDealDamage(Event):
	def __init__(self, damageInstance, game):
		super().__init__(game)
		self.damageInstance = damageInstance

	def betweenSubscriberTypes(self):
		self.damageInstance.update()
		self.canceled = self.newCanceled or self.damageInstance.canceled

class PhaseTakeDamage(Event):
	pass

class EventTakeDamage(Event):
	def __init__(self, damageInstance, game):
		super().__init__(game)
		self.damageInstance = damageInstance

	def betweenSubscriberTypes(self):
		self.damageInstance.update()
		self.canceled = self.newCanceled or self.damageInstance.canceled

class PhasePostDamage(Event):
	pass

class PhaseEndTurns(Event):
	pass

class EventSubscription:
	def __init__(self, eventClass, subscriber, function, order=0):
		self.eventClass = eventClass
		self.subscriber = subscriber
		self.function = function
		self.order = order

class EventSubscriber(ABC):
	def __init__(self):
		self.subscribedEvents = []

	def subscribeEvent(self, eventClass, function, order=0):
		self.subscribedEvents.append(EventSubscription(eventClass, self, function, order))
