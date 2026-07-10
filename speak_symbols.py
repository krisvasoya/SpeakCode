class Environment:
    def __init__(self, parent: 'Environment' = None):
        self.variables = {}
        self.parent = parent

    def define(self, name: str, value: any):
        """Define a variable in the current scope."""
        if name in self.variables:
            raise ValueError(f"Variable '{name}' is already defined in the current scope.")
        self.variables[name] = value

    def lookup(self, name: str) -> any:
        """Get the value of a variable, looking up the parent chain if necessary."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.lookup(name)
        raise KeyError(f"Variable '{name}' is not defined.")

    def update(self, name: str, value: any):
        """Update an existing variable value, searching up the parent chain."""
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            self.parent.update(name, value)
            return
        raise KeyError(f"Variable '{name}' is not defined. Use 'define' to create it first.")

    def is_defined_locally(self, name: str) -> bool:
        """Check if a variable is defined specifically in this scope."""
        return name in self.variables

    def is_defined(self, name: str) -> bool:
        """Check if a variable is defined recursively in this or parent scopes."""
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.is_defined(name)
        return False
