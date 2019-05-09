import os, gtts, PIL, praw, PIL.Image, PIL.ImageDraw, PIL.ImageFont, moviepy.editor, shutil

class program: #the main class
    class output: #the class for controlled stdout within the program
        outputEnabled = True #controls whether or not to print controlled output lines
        def print(string) -> None: #will only print if <program.output.outputEnabled == True>.
            if (program.output.outputEnabled):
                print (string)
    class tts: #the class for text to speech stuff
        def makeTTSFile(ttsText, language = 'en') -> str: #this outputs a .mp3 file and returns the path
            try:
                currentNumberCount = int(str(open('./tts-file-count-number.txt').read()))
            except:
                currentNumberCount = 1
            file = open('./tts-file-count-number.txt', 'w')
            file.write(str(currentNumberCount + 1))
            file.close()
            if ('tmp' not in os.listdir('.')):
                os.mkdir('tmp')
            filePath = './tmp/{}.mp3'.format(str(currentNumberCount))
            textToSpeech = gtts.gTTS(text = str(ttsText), lang = language)
            textToSpeech.save(filePath)
            return filePath
    class reddit: #the class that has the functions and data that has to do with reddit
        reddit = praw.Reddit('bot1', user_agent = 'bot1 user agent')
        def getRepliesFromTopPost() -> dict: #returns a list of the post's replies sorted by their score
            comments = {}
            sbmsn = None
            for submission in program.reddit.reddit.subreddit('askreddit').hot(limit = 1):
                sbmsn = submission
                for comment in submission.comments:
                    try:
                        isAscii = True
                        normalChars = [ #I dont know any better way to do this so I had to hardcode it
                            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '`', '~', '!',
                            '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '{', '}',
                            '|', '\\', '"', "'", ';', ':', ',', '<', '>', '.', '/', '?', ' ',
                                    '-', '_', '+', '=', '\n'
                        ]
                        for each in str(comment.body): #nested for loop paradise...
                            if (each.lower() in normalChars):
                                pass
                            else:
                                isAscii = False
                        if (isAscii):
                            comments[int(comment.score)] = str(comment.body)
                    except:
                        pass
            return [comments, sbmsn]
    class presets: #the class for the configuration variables
        numberOfAskredditCommentsToShow = 10 #will show the top x amount of comments from the post.
    class utils:
        def asciitize(string):
            normalChars = [ #I dont know any better way to do this so I had to hardcode it
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '`', '~', '!',
                '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '{', '}',
                '|', '\\', '"', "'", ';', ':', ',', '<', '>', '.', '/', '?', ' ',
                '-', '_', '+', '=', '\n'
            ]
            newString = ''
            for each in string:
                if (each.lower() in normalChars):
                    pass
                else:
                    each = '?'
                newString += each
            return newString
    class images: #the class that has the functions for generating images
        def generateImageWithTextOnIt(text, dimensions = [1920, 1080], bgcolor = 'white', fgcolor = 'black'): #generates an image that can later be stitched into the video
            image = PIL.Image.new('RGB', (dimensions[0], dimensions[1]), bgcolor)
            text = text.replace('\n', '')
            newText = []
            tmpText = ''
            last = 1
            lineWidthInChars = 50 #make the lines 50 characters long each
            for each in text: #split the string into 50 characer long segments
                last += 1
                tmpText = str(tmpText) + str(each)
                if (last >= lineWidthInChars):
                    last = 1
                    tmpText += '-'
                    newText.append(tmpText)
                    tmpText = ''
            if (tmpText != ''):
                newText.append(tmpText)
            if ('tmp' not in os.listdir('.')):
                os.mkdir('tmp')
            try:
                currentNumberCount = int(str(open('./image-file-count-number.txt').read()))
            except:
                currentNumberCount = 1
            file = open('./image-file-count-number.txt', 'w')
            file.write(str(currentNumberCount + 1))
            file.close()
            filePath = './tmp/{}.png'.format(str(currentNumberCount))

            textTopYCoordinate = 0 #int(image.size[1] / 4) #there will be no text above this y coordinate
            textHeight = int(image.size[1] - textTopYCoordinate)
            textHeight /= len(newText)
            if (textHeight > (image.size[0] / 30)):
                textHeight = int(image.size[0] / 30)
            font = PIL.ImageFont.truetype('./utils/default-font.ttf', int(textHeight))
            draw = PIL.ImageDraw.Draw(image)
            lastYCoord = textTopYCoordinate
            for textLine in newText:
                textSize = draw.textsize(textLine, font = font)
                textCoords = [0, 0]
                textCoords[0] = int((image.size[0] - textSize[0]) / 2)
                textCoords[1] = int(lastYCoord)
                lastYCoord += textSize[1]
            if (lastYCoord % 2 == 0):
                pass
            else:
                lastYCoord += 1
            image = image.resize((dimensions[0], lastYCoord), PIL.Image.ANTIALIAS)
            lastYCoord = textTopYCoordinate
            font = PIL.ImageFont.truetype('./utils/default-font.ttf', int(textHeight))
            draw = PIL.ImageDraw.Draw(image)
            for textLine in newText:
                textSize = draw.textsize(textLine, font = font)
                textCoords = [0, 0]
                textCoords[0] = int((image.size[0] - textSize[0]) / 2)
                textCoords[1] = int(lastYCoord)
                draw.text(textCoords, textLine, fgcolor, font = font)
                lastYCoord += textSize[1]
            newImage = PIL.Image.new('RGB', (dimensions[0], dimensions[1]), bgcolor)
            '''if (image.size[1] > newImage.size[1]):
                aspectRatio = image.size[0] / image.size[1]
                newImageSize = [0, 0]
                newImageSize[0] = int(newImage.size[0] * aspectRatio)
                newImageSize[1] = int(newImage.size[1] / aspectRatio)
                image = image.resize((*newImageSize), PIL.Image.ANTIALIAS)'''#fix the resizing method so that the image doesnt overflow on the y axis
            newImageCoords = [int((newImage.size[0] - image.size[0]) / 2), int((newImage.size[1] - image.size[1]) / 2)]
            newImage.paste(image, newImageCoords)
            newImage.save(filePath)
            return filePath

program.output.print('Program started.')
program.output.print('Getting the comments from the top askreddit post.')
askRedditCommentList = program.reddit.getRepliesFromTopPost()

commentUpvotesSorted = sorted(askRedditCommentList[0])
commentUpvotesSorted.reverse()

program.output.print(program.utils.asciitize('Found a post titled "{}" with {} upvotes that is in hot.'.format(askRedditCommentList[1].title, askRedditCommentList[1].score)))

if (program.presets.numberOfAskredditCommentsToShow > len(commentUpvotesSorted)):
    program.output.print('The number of comments you chose to display was larger than the amount of available comments - <program.presets.numberOfAskredditCommentsToShow> was changed to the max amount of comments and nothing more.')
    program.presets.numberOfAskredditCommentsToShow = len(commentUpvotesSorted)

topComments = {}
topCommentsUpvotesSorted = []

iterationStage = 0
while (iterationStage < program.presets.numberOfAskredditCommentsToShow):
    topComments[commentUpvotesSorted[iterationStage]] = askRedditCommentList[0][commentUpvotesSorted[iterationStage]]
    topCommentsUpvotesSorted.append(commentUpvotesSorted[iterationStage])
    iterationStage += 1

ttsFilePathsInOrderOfTopCommentsSortedByUpvotes = [program.tts.makeTTSFile(askRedditCommentList[1].title)] #10/10 file naming :)
iterationStage = 0
for comment in topComments:
    iterationStage += 1
    program.output.print('Making TTS file {}/{}.'.format(str(iterationStage), str(len(topComments))))
    commentText = topComments[comment]
    ttsPath = program.tts.makeTTSFile(commentText)
    ttsFilePathsInOrderOfTopCommentsSortedByUpvotes.append(ttsPath)

imageFilePathsInOrderOfTopCommentsSortedByUpvotes = [program.images.generateImageWithTextOnIt(askRedditCommentList[1].title, fgcolor = '#9494FF')] #sorry :)
iterationStage = 0
for comment in topComments:
    iterationStage += 1
    program.output.print('Making image file {}/{}.'.format(str(iterationStage), str(len(topComments))))
    imagePath = program.images.generateImageWithTextOnIt(topComments[comment], fgcolor = '#ff4301')
    imageFilePathsInOrderOfTopCommentsSortedByUpvotes.append(imagePath)

outputMp4List = []
for each in range(len(imageFilePathsInOrderOfTopCommentsSortedByUpvotes)):
    program.output.print('Stitching together audio and video files ({}/{}).'.format(str(each + 1), str(len(imageFilePathsInOrderOfTopCommentsSortedByUpvotes))))
    imagePath = imageFilePathsInOrderOfTopCommentsSortedByUpvotes[each]
    audioPath = ttsFilePathsInOrderOfTopCommentsSortedByUpvotes[each]
    os.system('ffmpeg.exe -loop 1 -i {} -i {} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest ./tmp/out{}.mp4'.format(imagePath, audioPath, str(each)))
    outputMp4List.append('./tmp/out{}.mp4'.format(str(each)))

program.output.print('Stitching together the videos.')

videoFileList = []
for each in outputMp4List:
    videoFileList.append(moviepy.editor.VideoFileClip(each))
finalVideo = moviepy.editor.concatenate_videoclips(videoFileList)
finalVideo.write_videofile('output.mp4')

program.output.print('Done!')

shutil.rmtree('tmp')