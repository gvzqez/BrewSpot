from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Locals, Beers, Store, User

engine = create_engine('sqlite:///brewspot.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Beers
moritz = Beers(name="Moritz", origin='CAT', description="Moritz Beer", price=2.50, logo="https://hangar.org/webnou/wp-content/uploads/2012/02/logo-moritz.jpg")
session.add(moritz)
session.commit()

damm = Beers(name="Estrella Damm", origin='CAT', description="Estrella Damm Beer", price=1.50, logo="https://botw-pd.s3.amazonaws.com/styles/logo-thumbnail/s3/102014/estrella_damm1.png?itok=8mL6yVcI")
session.add(damm)
session.commit()

galicia = Beers(name="Estrella Galicia", origin='SP', description="Estrella Galicia", price=2.00, logo="https://www.singlutenismo.com/wp-content/uploads/logo-estrella-galicia2.png")
session.add(galicia)
session.commit()

san_miguel = Beers(name="San Miguel", origin='SP', description="San Miguel Beer", price=1.50, logo="https://pbs.twimg.com/profile_images/612995382340153345/bkfmBVXG_400x400.png")
session.add(san_miguel)
session.commit()

asahi = Beers(name="Asahi", origin='JP', description="Asahi Beer", price=3, logo="https://static.wixstatic.com/media/44aa7b_b51002ed121d408183573ae3636fd49f~mv2.jpeg/v1/fill/w_490,h_268,al_c,q_80,usm_0.66_1.00_0.01/44aa7b_b51002ed121d408183573ae3636fd49f~mv2.webp")
session.add(asahi)
session.commit()


# Locals
timesburg = Locals(name="Timesburg", description="Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante.")
timesburg.stores.append(moritz)
session.add(timesburg)
session.commit()

parking_pizza = Locals(name="Parking Pizza", description="Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante.")
parking_pizza.stores.append(galicia)
session.add(parking_pizza)
session.commit()

kibuka = Locals(name="Kibuka", description="Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante.")
kibuka.stores.append(san_miguel)
kibuka.stores.append(asahi)
session.add(kibuka)
session.commit()


# Users
admin0 = User(username="admin0", email="gerard.vazquez.fabregat@gmail.com", local_id=1)
session.add(admin0)
session.commit()

admin1 = User(username="admin1", email="test0@gmail.com", local_id=2)
session.add(admin1)
session.commit()

admin2 = User(username="admin2", email="test1@gmail.com", local_id=3)
session.add(admin2)
session.commit()



