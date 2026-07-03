from sqlalchemy import Column, String, Boolean, Integer, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
#do we need both of the above declartive bases?

Base = declarative_base()


# Users table
class User(Base):
    __tablename__ = "users"
    
    sql_id = Column(Integer, primary_key=True)
    user_id = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    is_child = Column(Boolean, nullable=True)  # SQL Server BIT
    restricted_tags = Column(String(200), nullable=True)
    liked_cat = Column(String(200), nullable=True)


# Optional User Map table
class user_map(Base):
    __tablename__ = "user_map"
    
    sql_id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=True)
    hashed_password = Column(String(200), nullable=True)
    name = Column(String(100), nullable=True)
    is_child = Column(Boolean, nullable=True)

#do we need restricted tags for user_map will we implemented this and liked_cat

# Content table
class Content(Base):
    __tablename__ = "content"
    
    sql_id = Column(Integer, primary_key=True)  # identity column
    content_id = Column(String(50), unique=True, nullable=False)  # business ID
    category = Column(String(50), nullable=True)
    sub_category = Column(String(50), nullable=True)
    title = Column(Text, nullable=True) 
    abstract = Column(Text, nullable=True) 
    is_harmful = Column(Boolean, nullable=True)
    harm_category = Column(String(500), nullable=True)



# Ranked Recommendations table
class RankedRecommendation(Base):
    __tablename__ = "ranked_recommendations"
    
    sql_id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=True)
    content_id = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    sub_category = Column(String(50), nullable=True)
    title = Column(String(500), nullable=True)
    abstract = Column(Text, nullable=True)



# Interactions table
class Interaction(Base):
    __tablename__ = "interactions"
    
    sql_id = Column(Integer, primary_key=True, autoincrement=True)  # identity column
    user_id = Column(String(50), nullable=True)
    content_id = Column(String(50), nullable=True)
    interaction_type = Column(String(50), nullable=True)
    interaction_date = Column(Date, nullable=True)


