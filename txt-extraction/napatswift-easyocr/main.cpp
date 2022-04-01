#include <string>
#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>
#include <opencv2/opencv.hpp>
#include <filesystem>
#include <fstream>

using namespace cv;

std::string splitFileName(std::string filepath){
    size_t start = filepath.rfind('/');
    size_t end = filepath.rfind('.');
    return filepath.substr(start+1, end-start-1);
}

std::vector<Rect> lineBlock(std::string srcPath){
    Mat src = imread(srcPath);

    if (src.empty()){
        std::cerr << "[error]: image " << srcPath << " is empty" << std::endl;
        return ;
    }

    std::string destPath = splitFileName(srcPath);

    Mat dest;
    src.copyTo(dest);

    cvtColor(src, src, COLOR_BGR2GRAY);
    src = src < 200;
    // threshold(src, src, 200, 250, THRESH_OTSU|THRESH_BINARY_INV);

    Mat kernel = getStructuringElement(MORPH_CROSS, Size(1, 5));
    dilate(src, src, kernel);

    Mat1f horProj;
    reduce(src, horProj, 1, REDUCE_AVG);
    Mat1b hist = horProj <= 0;

    // if (!contours.empty()) contours.clear();

    // findContours(src, contours, RETR_EXTERNAL, CHAIN_APPROX_NONE);
    int prev_r = -1;
    bool isSpace = true;
    size_t lineNumber = 0;
    std::vector<Rect> lineBounds;
    for (size_t r = 0; r < src.rows; r++){
        if (isSpace){
            if (!hist(r)){
                isSpace = false;
                prev_r = r;
            }
        } else {
            if (hist(r)){
                isSpace = true;
                lineBounds.push_back(Rect(Point(0, r), Point(src.cols, prev_r)));
            }
        }
    }

    // imwrite("./output/2022-3_3-2/" + destPath + ".jpg", dest);
    // std::cout << "number of blocks on "<< destPath << ": " << contours.size() << std::endl;
    return lineBounds;
}
 
int main(int argc, char* argv[])
{
    // std::string outText;
    // Mat image;

    // std::ofstream fileOutput;
    // fileOutput.open("./output/ocr_thb_gray.csv");
    // fileOutput << "text,br.x,br.y,tl.x,tl.y" << std::endl;

    tesseract::TessBaseAPI *tessOcr = new tesseract::TessBaseAPI();
    tessOcr->Init(NULL, "tha+eng", tesseract::OEM_LSTM_ONLY);
    tessOcr->SetPageSegMode(tesseract::PSM_SINGLE_LINE);

    std::string path = std::__fs::filesystem::absolute("./input/2022_3-5");
    for (const auto &entry : std::__fs::filesystem::directory_iterator(path)){
        std::vector<std::vector<Point>> contours;
        lineBlock(entry.path(), contours);
    }

    // image  = imread("./input/thb_gray.jpg");
    // lineBlock("./input/2022_3-5/page-22.jpg");

    
    // for (const std::vector<Point> contour: contours){
    //     Rect bound = boundingRect(contour);

    //     if (bound.area() < 100) continue;

    //     Mat croped = image(bound);
    //     rectangle(im, bound, Scalar(0, 0, 255), 3);

    //     ocr->SetImage(croped.data, croped.cols, croped.rows, 3, croped.step);
    //     outText = std::string(ocr->GetUTF8Text());
        
    //     if (outText[outText.length()-1] == '\n')
    //         outText.erase(outText.length()-1);
        
    //     if (outText.empty())
    //         continue;

    //     if (outText.find(',') == std::string::npos){
    //         fileOutput << outText;
    //     } else {
    //         fileOutput << "\"" << outText << "\"";
    //     }

    //     fileOutput << ',' << bound.br().x << ',' << bound.br().y << ',' << bound.tl().x << ',' << bound.tl().y;
    //     fileOutput << std::endl;
    // }

    // if (fileOutput.is_open()){
    //     fileOutput.close();
    // }

	tessOcr->End();
    // destroyAllWindows();
    return EXIT_SUCCESS;
}