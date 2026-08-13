from Networksecurity.components.data_ingesion import DataIngestion
from Networksecurity.exception.exception import NetworkSecurityException
from Networksecurity.logging.logger import logger
from Networksecurity.entity.config_entity import DataIngestionConfig
from Networksecurity.entity.config_entity import TrainingPipelineConfig
import sys
if __name__=="__main__":
    try:
        trainingpipelineconfig=TrainingPipelineConfig()
        dataingesionconfig=DataIngestionConfig(training_pipeline_config=trainingpipelineconfig)
        data_ingesion=DataIngestion(data_ingestion_config=dataingesionconfig)
        logger.info("Initiating the data_ingesion process(Reading the data from mongodb atlas and then converting it into teh train test split an dplacing it inside teh files or csvs)")
        dataingestionartifact=data_ingesion.initiate_data_ingestion()
        print(dataingestionartifact)
        logger.info("data ingesion main done")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
