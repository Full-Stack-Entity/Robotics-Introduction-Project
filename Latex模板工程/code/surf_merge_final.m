% 基于surf特征点检测的多图像拼接程序
clc; clear; close all;%清除程序运行之前存在的变量和图片

% 设置图像文件夹路径，依次读取
imgFolder = 'Simple';
imgFiles = dir(fullfile(imgFolder, '*.jpg')); 
nImages = length(imgFiles);%计算图片的个数

% 读取图像，将他们按顺序存储到images元胞数组中
images = cell(1, nImages);
for i = 1:nImages
    images{i} = imread(fullfile(imgFolder, imgFiles(i).name));
end

%按顺序依次两两拼接所有图像
panorama=images{1};
for i=2:nImages
    panorama=two_picture_stitching(panorama,images{i});
    %two_picture_stitiching函数的定义在下面
end

% 显示拼接完成得到的图像，并将拼接结果保存
figure; 
imshow(panorama); 
title('多图拼接结果');
imwrite(panorama,'result.jpg');

function panorama=two_picture_stitching(I1,I2)%I1，I2为进行拼接的两图像
    gray1 = rgb2gray(I1);
    gray2 = rgb2gray(I2);

    % 检测两张图片的 SURF 特征
    points1 = detectSURFFeatures(gray1);
    points2 = detectSURFFeatures(gray2);

    % 通过非极大值筛选出有效特征点到validPoints中并提取其特征描述子到features中
    [features1, validPoints1] = extractFeatures(gray1, points1);
    [features2, validPoints2] = extractFeatures(gray2, points2);

    % 匹配两组图像的特征点并保留可以配对的特征点到matchPoints中
    indexPairs = matchFeatures(features1, features2, 'Unique', true);
    matchedPoints1 = validPoints1(indexPairs(:,1));
    matchedPoints2 = validPoints2(indexPairs(:,2));

    % 可视化匹配点
    figure;
    showMatchedFeatures(I1, I2, matchedPoints1, matchedPoints2, 'montage');
    title('匹配特征点');

    % 通过可匹配的特征点估计两张图之间的旋转关系，用一个3*3的正交矩阵tform表示（使用 RANSAC 自动剔除错误匹配）
    tform = estimateGeometricTransform2D(...
    matchedPoints2, matchedPoints1, 'projective');
 % 结合旋转矩阵tform计算输出图像尺寸
    % 获取经过旋转调整后的图像2的边界范围
    xlim=[1 size(I2,2)];
    ylim=[1 size(I2,1)];
    [xx, yy] = meshgrid(xlim, ylim);
    [cornersX, cornersY] = transformPointsForward(tform, xx(:), yy(:));

    % 结合图像1和变换后的图像2的边界，计算拼接所得的图像的边界
    xMin = floor(min([1; cornersX]));
    xMax = ceil(max([size(I1,2); cornersX]));
    yMin = floor(min([1; cornersY]));
    yMax = ceil(max([size(I1,1); cornersY]));

    % 生成outputView记录内部坐标与世界坐标之间的关系
    width  = xMax - xMin + 1;
    height = yMax - yMin + 1;
    outputView = imref2d([height width], [xMin xMax], [yMin yMax]);

    % 使用imwarp函数和两幅图片对世界坐标的旋转关系,将I1和I2分别映射到合成所得的大图中
    warpedImage2 = imwarp(I2, tform, 'OutputView', outputView);
    warpedImage1 = imwarp(I1, affine2d(eye(3)), 'OutputView', outputView);    
%构建权重并将两图像恰当融合，避免产生灰度突变等问题
    % 创建掩码：非纯黑区域为有效像素
    mask1 = any(warpedImage1 > 0, 3);
    mask2 = any(warpedImage2 > 0, 3);

    % 以距离为标准给各点设置权重
    weight1 = double(bwdist(~mask1));
    weight2 = double(bwdist(~mask2));
    sumWeight = weight1 + weight2 + eps;
    w1s = weight1 ./ sumWeight;
    w2s = weight2 ./ sumWeight;
    w1=cat(3,w1s,w1s,w1s);
    w2=cat(3,w2s,w2s,w2s);    

    % 基于所得权重融合两图像
    panorama=uint8(w1 .* double(warpedImage1) + w2 .* double(warpedImage2));   
end