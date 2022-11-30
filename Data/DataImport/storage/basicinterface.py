import sys


class BasicInterface:

    @classmethod
    def cls_from_name(cls, cls_type: str, issubcl=True):
        """
        Get type of class from string (subclass of instance)
        Returns None if non-existent.
        @param cls_type: class name
        @param issubclass: if class is subclass or not
        @return: class type
        """
        if issubcl:
            return cls.subcl_from_name(cls_type)

        for mod in sys.modules.values():
            if hasattr(mod, cls_type):
                return getattr(mod, cls_type)
        return None

    @classmethod
    def from_name(cls, cls_type: str, issubcl=True, **kwargs):
        """
        Get instance of class from string (subclass of interface)
        Returns None if non-existent.
        @param cls_type: class name
        @param issubclass: class is subclass of current class
        @return: instance
        """
        return cls.cls_from_name(cls_type, issubcl)(**kwargs) if cls.cls_from_name(cls_type, issubcl) is not None else None

    def _set_attrs(self, **kwargs):
        """
        Set attributes of class - override if necessary
        """
        for name, val in kwargs.items():
            setattr(self, name, val)

    def _get_attrs(self):
        """
        Get attributes of class - override if necessary
        """
        return self.__dict__

    @classmethod
    def _get_subclasses(cls, list_subclasses=[]):
        """
        Recursively get subclasses.
        @param list_subclasses: needed for recursion
        @return: list of subclass types
        """
        for subclass in cls.__subclasses__():
            subclass._get_subclasses(list_subclasses)
            list_subclasses.append(subclass)
        return list_subclasses

    @classmethod
    def subcl_from_name(cls, cls_type: str):
        """
        Get type of class from string (subclass of instance)
        Returns None if non-existent.
        @param cls_type: class name
        @return: class type
        """
        if cls_type == cls.__name__:
            return cls
        for subcl in cls._get_subclasses():
            if cls_type == subcl.__name__:
                return subcl
        return None