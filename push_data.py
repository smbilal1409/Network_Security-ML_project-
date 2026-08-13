import os
import json
import certifi
import pandas as pd
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

from Networksecurity.logging.logger import logger
from Networksecurity.exception.exception import NetworkSecurityException


# Load environment variables
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

ca = certifi.where()


class ETLPipeline:

    def __init__(self):
        try:
            logger.info("Initializing ETL Pipeline")

            self.mongo_url = MONGO_DB_URL

            if not self.mongo_url:
                raise ValueError(
                    "MONGO_DB_URL is not set in .env file"
                )

            self.client = MongoClient(
                self.mongo_url,
                tlsCAFile=ca
            )

            # Test MongoDB connection
            self.client.admin.command("ping")

            logger.info("MongoDB connection successful")

        except Exception as e:
            logger.error("Error while connecting to MongoDB")
            raise NetworkSecurityException(e,sys)


    def extract_data(self, file_path):
        """
        Extract data from CSV file.
        """

        try:
            logger.info("Starting data extraction")

            dataframe = pd.read_csv(file_path)

            logger.info(
                f"Data extracted successfully. "
                f"Number of records: {len(dataframe)}"
            )

            return dataframe

        except Exception as e:
            logger.error(
                f"Error while extracting data from CSV: {e}"
            )

            raise NetworkSecurityException(e,sys)


    def transform_data(self, dataframe):
        """
        Transform DataFrame into JSON-compatible records.
        """

        try:
            logger.info("Starting data transformation")

            # Convert DataFrame into list of dictionaries
            records = dataframe.to_dict(
                orient="records"
            )

            # Convert records into JSON-compatible data
            json_data = json.loads(
                json.dumps(
                    records,
                    default=str
                )
            )

            logger.info(
                f"Data transformation completed. "
                f"Number of records: {len(json_data)}"
            )

            return json_data

        except Exception as e:
            logger.error(
                f"Error while transforming data: {e}"
            )

            raise NetworkSecurityException(e,sys)


    def load_data(
        self,
        data,
        database_name,
        collection_name
    ):
        """
        Load transformed data into MongoDB.
        """

        try:
            logger.info("Starting data loading into MongoDB")

            database = self.client[database_name]

            collection = database[collection_name]

            if data:

                result = collection.insert_many(data)

                logger.info(
                    f"Successfully inserted "
                    f"{len(result.inserted_ids)} records "
                    f"into MongoDB"
                )

            else:

                logger.warning(
                    "No data available to insert"
                )

        except Exception as e:
            logger.error(
                f"Error while loading data into MongoDB: {e}"
            )

            raise NetworkSecurityException(e,sys)


    def run_pipeline(
        self,
        csv_path,
        database_name,
        collection_name
    ):
        """
        Run complete ETL pipeline.
        """

        try:

            logger.info("========== ETL PIPELINE STARTED ==========")

            # -------------------------
            # EXTRACT
            # -------------------------
            dataframe = self.extract_data(
                csv_path
            )

            # -------------------------
            # TRANSFORM
            # -------------------------
            json_data = self.transform_data(
                dataframe
            )

            # -------------------------
            # LOAD
            # -------------------------
            self.load_data(
                json_data,
                database_name,
                collection_name
            )

            logger.info(
                "========== ETL PIPELINE COMPLETED SUCCESSFULLY =========="
            )

        except Exception as e:

            logger.error(
                f"ETL Pipeline failed: {e}"
            )

            raise NetworkSecurityException(e,sys)

        finally:

            self.client.close()

            logger.info(
                "MongoDB connection closed"
            )


if __name__ == "__main__":

    try:

        logger.info("Starting ETL application")

        pipeline = ETLPipeline()
        pipeline.run_pipeline(
            csv_path="Network_data/phisingData.csv",
            database_name="network_security",
            collection_name="phishing_data"
            )


        

    except Exception as e:

        logger.error(
            f"ETL application failed: {e}"
        )

