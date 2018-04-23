class Item:
    def __init__(self, use_function=None, targeting=None, targeting_message=None, quantity=None, max_charge_time=None,
                 **kwargs):
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.quantity = quantity
        self.max_charge_time = max_charge_time
        self.charge_time = 0
        self.function_kwargs = kwargs
