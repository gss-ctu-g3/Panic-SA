from pymongo import AsyncMongoClient
from fastapi import FastAPI

from schemas import EmergencyContact


app = FastAPI()


# client = AsyncMongoClient(os.environ["MONGODB_URL"],server_api=pymongo.server_api.ServerApi(version="1", strict=True,deprecation_errors=True))
client = AsyncMongoClient("mongodb+srv://thepcninja77_db_user:0tOjAc6eLoRbIngC@dev.dlzknxm.mongodb.net/")
db = client.get_database("panic_sa")
collection_contacts = db.get_collection("contacts")



# # Represents an ObjectId field in the database.
# # It will be represented as a `str` on the model so that it can be serialized to JSON.
# PyObjectId = Annotated[str, BeforeValidator(str)]

# class StudentModel(BaseModel):
#     """
#     Container for a single student record.
#     """

#     # The primary key for the StudentModel, stored as a `str` on the instance.
#     # This will be aliased to ``_id`` when sent to MongoDB,
#     # but provided as ``id`` in the API requests and responses.
#     id: Optional[PyObjectId] = Field(alias="_id", default=None)
#     name: str = Field(...)
#     email: EmailStr = Field(...)
#     course: str = Field(...)
#     gpa: float = Field(..., le=4.0)
#     model_config = ConfigDict(
#         populate_by_name=True,
#         arbitrary_types_allowed=True,
#         json_schema_extra={
#             "example": {
#                 "name": "Jane Doe",
#                 "email": "jdoe@example.com",
#                 "course": "Experiments, Science, and Fashion in Nanophotonics",
#                 "gpa": 3.0,
#             }
#         },
#     )



# class UpdateStudentModel(BaseModel):
#     """
#     A set of optional updates to be made to a document in the database.
#     """

#     name: Optional[str] = None
#     email: Optional[EmailStr] = None
#     course: Optional[str] = None
#     gpa: Optional[float] = None
#     model_config = ConfigDict(
#         arbitrary_types_allowed=True,
#         json_encoders={ObjectId: str},
#         json_schema_extra={
#             "example": {
#                 "name": "Jane Doe",
#                 "email": "jdoe@example.com",
#                 "course": "Experiments, Science, and Fashion in anophotonics",
#                 "gpa": 3.0,
#             }
#         },
#     )



# class StudentCollection(BaseModel):
# """
# A container holding a list of `StudentModel` instances
# """

# students: List[StudentModel]



# @app.post(
#     "/students/",
#     response_description="Add new student",
#     response_model=StudentModel,
#     status_code=status.HTTP_201_CREATED,
#     response_model_by_alias=False,
# )
# async def create_student(student: StudentModel = Body(...)):
#     """
#     Insert a new student record.

#     A unique ``id`` will be created and provided in the response.
#     """
#     new_student = student.model_dump(by_alias=True, exclude=["id"])
#     result = await student_collection.insert_one(new_student)
#     new_student["_id"] = result.inserted_id

#     return new_student



#route
#make contact
#give id



@app.post("/contacts")
def create_emergency_contact(contact_json: EmergencyContact):
    """
    Create an emergency contact in database
    """
    pass
    print(contact_json)