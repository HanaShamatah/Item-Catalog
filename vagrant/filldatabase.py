from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_database import Base, Categories, CatalogItem, User

engine = create_engine('sqlite:///categorieswithuser.db')
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


# Create dummy user
User1 = User(name="Hana Shamatah", email="hanashamata@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
categories1 = Categories(user_id=1, name="hair")

session.add(categories1)
session.commit()

catalogItem1 = CatalogItem(user_id=1, category_name="hair", name="Accessories",
                           description="prety blond hair")
session.add(catalogItem1)
session.commit()


User2 = User(name="hana shamatah", email="hanashamata31@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User2)
session.commit()

# Menu for UrbanBurger
categories2 = Categories(user_id=2, name="body")

session.add(categories2)
session.commit()

catalogItem2 = CatalogItem(user_id=2, category_name="body", name="BodyCare",
                           description="Softness products")
session.add(catalogItem2)
session.commit()
print "added menu items!"
