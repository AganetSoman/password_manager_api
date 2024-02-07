from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker



connection_string = URL.create(
    'postgresql',
    username='aganetsoman23',
    password='mYClUFw6OD3q',
    host='ep-wandering-lake-a1bw53rb.ap-southeast-1.aws.neon.tech',
    database='password_db',

)

engine = create_engine(connection_string)
# engine = create_engine(url)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()
