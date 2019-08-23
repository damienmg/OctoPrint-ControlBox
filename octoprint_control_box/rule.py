
class Chainable(object):
    def __init__(self, name, *args):
        self._name = name
        self._chains = list(args)

    def name(self):
        return self._name

    def chain(self, action):
        self._chains.append(action)
        return self

    def execute(self):
        value = True
        for action in self._chains:
            if not action.execute():
                value = False
        return value

class Action(Chainable):
    def __init__(self, name):
        super(Action, self).__init__(name)

    def do(self):
        pass
    
    def execute(self):
        if self.do():
            return super(Action, self).execute()
        return False

class Condition(Chainable):
    def __init__(self, name):
        super(Condition, self).__init__(name)

    def is_true(self):
        return False

    def execute(self):
        if self.is_true():
            return super(Condition, self).execute()
        return False

class NotCondition(Condition):
    def __init__(self, arg):
        super(NotCondition, self).__init__("not(%s)" % arg.name())
        self._condition = arg

    def is_true(self):
        return not self.condition.is_true()

class AnyCondition(Condition):
    def __init__(self, *conditions):
        super(AnyCondition, self).__init__("any(%s)" % ", ".join([c.name() for c in conditions]))
        self._conditions = conditions


    def is_true(self):
        return any([c.is_true() for c in self._conditions])

class AllCondition(Condition):
    def __init__(self, *conditions):
        super(AllCondition, self).__init__("all(%s)" % ", ".join([c.name() for c in conditions]))
        self._conditions = conditions

    def is_true(self):
        return all([c.is_true() for c in self._conditions])

class LambdaAction(Action):
    def __init__(self, name, fn):
        super(LambdaAction, self).__init__(name)
        self._fn = fn
    
    def do(self):
        return self._fn()

class LambdaCondition(Condition):
    def __init__(self, name, fn):
        super(LambdaCondition, self).__init__(name)
        self._fn = fn

    def is_true(self):
        return self._fn()
