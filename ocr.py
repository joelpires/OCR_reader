import logging
import os
from logging import getLogger

import click
import pdf2image
from PIL import Image

from tesserocr import PyTessBaseAPI

logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('--input', help='It must be an image (JPEG or PNG) or a PDF file')
@click.option('--output', help='Name of the file to write the extracted text.')
@click.option('--verbose',
              help='To describe every step of the process.',
              is_flag=True)
def main(input, output, verbose):
    if verbose:
        logger.setLevel(logging.DEBUG)

    #Check if the file format is supported or not
    format = os.path.splitext(input)[1]
    supported = (format in ['.jpg', '.png', '.pdf', '.JPG', '.PNG', '.PDF'])

    if supported == False:
        logger.error('File must be an image (JPEG or PNG) or a PDF.')
    else:
        format = os.path.splitext(input)[1]
        logger.debug(f" File format is supported and is a {format}")

        if format in ['.jpg', '.png', '.JPG', '.PNG']:    #Image
            tesseract_ocr(input, output)

        else:    #PDF
            pages = pdf2image.convert_from_path(input)

            for number, page in enumerate(pages):
                if len(pages) == 1:
                    textfile = output
                else:
                    textfile = os.path.splitext(output)[0] + '_' + str(
                        number) + ".text"

                tesseract_ocr(page, textfile)


# Main algorithm that converts first to a b/w image and then extracts its text.
def tesseract_ocr(image, output):

    if isinstance(image, str):
        image = Image.open(image)

    logger.info('Pre-processing: Converting into a B/W Image.')
    image = image.convert('L').point(lambda x: 0 if x < 200 else 255, '1')

    logger.info('Extracting text...')
    with PyTessBaseAPI(lang='eng') as tesseract:
        tesseract.SetImage(image)
        logger.debug('Writing into a file.')
        fp = open(output, "w")
        fp.write(tesseract.GetUTF8Text())
        fp.close()

    logger.info('Text Extracted.')


if __name__ == '__main__':
    try:
        logger = getLogger(__name__)
        main()
    except Exception as e:
        logger.error(e)
