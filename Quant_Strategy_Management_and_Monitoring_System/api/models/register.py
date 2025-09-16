import sys
from typing import Callable, List

from loguru import logger
import importlib
from pathlib import Path

class ModelRegister:
    registered_labels: List[Callable] = []
    registered_containers: List[Callable] = []
    registered_characters: List[Callable] = []

    @staticmethod
    def load_all_characters():
        from characters.models import characters


        characters_path = Path(characters.__file__).parent

        for character_file in characters_path.iterdir():
            logger.info(f"MODELREGISTER: Scanning {character_file}")

            if '.py' not in character_file.name or '__' in character_file.name:
                continue

            file_name =  character_file.name.split('\\')[-1].replace('.py','')
            importlib.import_module(name=f'.{file_name}',package='characters.models.characters')

    @staticmethod
    def check_registered():
        if len(ModelRegister.registered_characters) == 0:
            logger.critical("MODELREGISTER: No registered characters found, you must have at least one registered character")
            sys.exit(1)

        if len(ModelRegister.registered_containers) == 0:
            logger.critical("MODELREGISTER: No registered containers found, you must have at least one registered container")
            sys.exit(1)

        if len(ModelRegister.registered_labels) == 0:
            logger.critical("MODELREGISTER: No registered labels found, you must have at least one registered label")
            sys.exit(1)


    @staticmethod
    def label_register(cls):
        logger.success(f"MODELREGISTER: Label registered {cls}")
        ModelRegister.registered_labels.append(cls)
        return cls

    @staticmethod
    def container_register(cls):
        logger.success(f"MODELREGISTER: Container registered {cls}")
        ModelRegister.registered_containers.append(cls)
        return cls


    @staticmethod
    def character_register(cls):
        ModelRegister.registered_characters.append(cls)
        logger.success(f"MODELREGISTER: Character registered {cls}")
        return cls


