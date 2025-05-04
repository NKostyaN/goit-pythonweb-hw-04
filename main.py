import argparse
import asyncio
from pathlib import Path
from aioshutil import copyfile
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# if file with the same name exists add index to it's name
async def check_name(path: Path, add: int = 0) -> Path:
    origin = path
    if add != 0:
        path = path.with_stem(f"{path.stem}_{str(add)}")
    if path.exists():
        return await check_name(origin, add + 1)
    else:
        return path


async def copy_file(file: Path, dest_path: Path) -> None:
    # extract file extension and make dir
    file_ext = file.suffix.removeprefix(".")
    new_dir = dest_path / file_ext
    new_dir.mkdir(parents=True, exist_ok=True)

    # check filename recursively
    new_file = await check_name(new_dir / file.name)

    await copyfile(file, new_file)  # just copy
    logging.info(f"Copied from \033[96m{file}\x1b[0m to --> \033[93m{new_file}\x1b[0m")


async def read_folder(src_path: Path, dest_path: Path) -> None:
    logging.info(f"Reading \033[92m{src_path}\x1b[0m")
    for child in src_path.iterdir():
        if child.is_file():
            await copy_file(child, dest_path)
        elif child.is_dir():
            await read_folder(child, dest_path)


async def main():
    # parsing args and check them
    parser = argparse.ArgumentParser(description="Sorting files by extension")

    try:  # try to parce
        parser.add_argument("source", help="Source folder")
        parser.add_argument("output", help="Destination folder")
        args = parser.parse_args()
        src_path = Path(args.source)
        dest_path = Path(args.output)
        try:  # try to make new folder and copy files
            dest_path.mkdir(parents=True, exist_ok=True)
            await read_folder(src_path, dest_path)
        except Exception as e:
            logging.info(e)
    except Exception as e:
        logging.info(
            f"{e}\nUse with 2 arguments \033[96m[source folder] [destination folder]\x1b[0m\n"
        )


if __name__ == "__main__":
    asyncio.run(main())
