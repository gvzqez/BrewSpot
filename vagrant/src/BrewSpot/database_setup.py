from sqlalchemy import Column, ForeignKey, Integer, Float, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    picture = Column(String, nullable=True)
    email = Column(String, index=True)
    local_id = Column(Integer, ForeignKey('locals.id'), nullable=False, default=0)



class Locals(Base):
    __tablename__ = 'locals'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)
    description = Column(String(500), nullable=False)
    stores = relationship('Beers', secondary='store')
    user = relationship('User')

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Beers(Base):
    __tablename__ = 'beers'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    origin = Column(String(5))
    description = Column(String(250))
    price = Column(Float)
    logo = Column(String(250), nullable=True)
    stores = relationship('Locals', secondary = 'store')

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'origin': self.origin,
            'description': self.description,
            'price': self.price,
            'logo': self.logo
        }


class Store(Base):
    __tablename__ = 'store'

    local_id = Column(Integer, ForeignKey('locals.id'), primary_key=True)
    beer_id = Column(Integer, ForeignKey('beers.id'), primary_key=True)
    available = Column(Boolean, nullable=False, default=True)


engine = create_engine('sqlite:///brewspot.db')

Base.metadata.create_all(engine)
