"""

Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner:
Secondary Owner:

"""

from abc import ABC, abstractmethod

class ColumnExpression(ABC):
  """
  Generates SQL against a column expression in a table
  """

  @abstractmethod
  def __init__(self):
    super().__init__()


  @property
  @abstractmethod
  def expression(self):
    """
    Represents an SQL column expression.
    Returns a reference to the underlying column expression.
    """
    pass

  @property
  @abstractmethod
  def type(self):
    """
    The database type of the underlying column expression
    """
    pass

  @property
  @abstractmethod
  def name(self):
    """
    The name or alias of the column expression
    """
    pass

  @property
  def table(self):
    """
    A reference to the database table that the ColumnExpression is bound to
    This may not necessarily return a TableExpression
    """
    pass

  @abstractmethod
  def compile(self, *args, **kw):
    """
    Compile the column expression into a sql string
    """
    pass

  @abstractmethod
  def __gt__(self, other):
    pass

  @abstractmethod
  def __lt__(self, other):
    pass

  @abstractmethod
  def __ge__(self, other):
    pass

  @abstractmethod
  def __le__(self, other):
    pass

  @abstractmethod
  def __eq__(self, other):
    pass

  @abstractmethod
  def __ne__(self, other):
    pass

  @abstractmethod
  def __and__(self, other):
    pass

  @abstractmethod
  def __or__(self, other):
    pass

  @abstractmethod
  def __invert__(self):
    pass

  @abstractmethod
  def __add__(self, other):
    pass

  @abstractmethod
  def __radd__(self, other):
    pass

  @abstractmethod
  def __sub__(self, other):
    pass

  @abstractmethod
  def __rsub__(self, other):
    pass

  @abstractmethod
  def __mul__(self, other):
    pass

  @abstractmethod
  def __rmul__(self, other):
    pass

  @abstractmethod
  def __truediv__(self, other):
    pass

  @abstractmethod
  def __rtruediv__(self, other):
    pass

  @abstractmethod
  def __floordiv__(self, other):
    pass

  @abstractmethod
  def __rfloordiv__(self, other):
    pass

  @abstractmethod
  def __mod__(self, other):
    pass

  @abstractmethod
  def __rmod__(self, other):
    pass


class TableExpression(ABC):
  """
  Generates SQL against all the columns in a table or the table itself
  """

  @abstractmethod
  def __init__(self, *args, **kw):
    super().__init__()

  @property
  @abstractmethod
  def t(self):
    #TODO: breaks LSP, consider removing this
    """
    Reference to the underlying Table in the expression
    """
    pass

  @property
  @abstractmethod
  def name(self):
    """
    name of the Table in the expression
    """
    pass

  @property
  @abstractmethod
  def c(self):
    """
    collection of ColumnExpressions
    """
    pass

  @property
  def columns(self):
    """
    alias for c
    """
    return self.c


  # These methods are not implemented for MVP-1
  def __gt__(self, other):
    raise NotImplementedError

  def __ge__(self, other):
    raise NotImplementedError

  def __lt__(self, other):
    raise NotImplementedError

  def __le__(self, other):
    raise NotImplementedError

  def __and__(self, other):
    raise NotImplementedError

  def __or__(self, other):
    raise NotImplementedError

  def __invert__(self):
    raise NotImplementedError

  def __eq__(self):
    raise NotImplementedError

  def __ne__(self):
    raise NotImplementedError

  def __xor__(self):
    raise NotImplementedError
