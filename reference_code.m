%% basic information of video to be processed
%CANON 70D has a FPS of 

clear all
close all
clc

readerobj = VideoReader('MVI_0379.MOV');
vid_Height = readerobj.Height; 
vid_Width = readerobj.Width;
nFrames = get(readerobj, 'NumberOfFrames');
FPS = get(readerobj, 'Framerate');
starting_frame = 210;
ending_frame = 545; %determine from the orignal video, rough calculation
% ending_frame = 1410;
numFrames = ending_frame-starting_frame;
vidFrames = read(readerobj, [starting_frame ending_frame]);%matrix to store image data of interest

%% empty matrices for storing data
mov(1:numFrames) = struct('cdata',zeros(vid_Height,vid_Width,3,'uint8'),'colormap',[]);
mov_gray(1:numFrames) = struct('cdata',zeros(vid_Height,vid_Width,3,'uint8'),'colormap',[]);
empty = struct('cdata',zeros(vid_Height,vid_Width,3,'uint8'),'colormap',[]);
empty.cdata = rgb2gray(empty.cdata);
empty = empty.cdata;


%% determine the center of the hole and an average diameter

mov(1).cdata=read(readerobj,starting_frame+1);
mov_gray(1).cdata = rgb2gray(mov(1).cdata);
image = mov_gray(1).cdata;
   
intial_x_crop = 445;
intial_y_crop = 88;    
x_max = 1160;
y_max = 932;%Select the height and width of the new view you want in pixels.

imgcrop = imcrop(image,[intial_x_crop intial_y_crop x_max y_max]);      
    
im_med = medfilt2(imgcrop,[15 15]);
    
canny=edge(im_med,'canny',[0.1 0.2],5);
test=bwareaopen(canny,100);
[row,col]=find(test);    
    
zz = length(row);
dia = zeros(1,zz);
center_x = sum(col)/zz;
center_y = sum(row)/zz;

imshow(imgcrop);
hold on
plot(col,row,'b*','markersize',3)
x_pos = x_max/100;
y_pos = y_max/100;
set(gcf,'PaperUnits','inches','PaperPosition',[0 0 x_pos y_pos])
fname = sprintf('finger_1.png');
savdir2 = 'C:\Users\slee\Documents\MATLAB\data of green particles\0.635mm 125particle\test\pics';
fullfileName=fullfile(savdir2,fname);
print('-dpng',fullfileName,'-r100');
    
for i = 1:zz
    dia(i) = sqrt((col(i)-center_x)^2+(row(i)-center_y)^2);
end

dia_ave = sum(dia)/zz;
ratio = dia_ave/(5/32); % scale from pixels dimension to inches
    
%% all the rest frames (bad frames at the beginning discarded)
count = 0;
for z = 5:numFrames
    mov(z).cdata=read(readerobj,starting_frame+z);
    mov_gray(z).cdata = rgb2gray(mov(z).cdata);
    image = mov_gray(z).cdata;    
   
    imgcrop = imcrop(image,[intial_x_crop intial_y_crop x_max y_max]);   
    im_med = medfilt2(imgcrop,[3 3]);
    canny=edge(im_med,'canny',[0.1 0.2],2.5);
    test=bwareaopen(canny,100);
%     test=bwareaopen(canny,zzz);
    [row,col]=find(test);
        
    %locate the max and min of distance
    len2 = length(row);
%     test=bwareaopen(canny,floor(len2/3));
    test=bwareaopen(canny,floor(len2/3));
    clear row;
    clear col;
    [row,col]=find(test);
    
    matr_cart=[col row];
    [cen_fit, radius_fit, residual]=fitcircle(matr_cart,'tol',1e-5);
    circ = 2*pi*radius_fit;
     
    len1 = length(row);
    min_col = min(col);
    max_col = max(col);
   
    i = min_col;
    angle1 = zeros(1,len1);
    dist = zeros(1,len1);
    while (i >= min_col & i <= max_col)
        k = 1;
        for j = 1:len1
            if col(j) == i
                col_temp(k) = col(j);
                row_temp(k) = row(j);
                coor_temp(k) = j;
                k = k+1;
            end
        end
        k = k-1;
        tan_temp = zeros(1,k);
        angle_temp = zeros(1,k);
        if i <= cen_fit(1)            
            for n = 1:k
                tan_temp(n) = (row_temp(n)-cen_fit(2))/(col_temp(n)-cen_fit(1));
                angle_temp(n) = atan(tan_temp(n))/pi*180+180;
                angle1(coor_temp(n)) = angle_temp(n);
                dist(coor_temp(n)) = sqrt((row(coor_temp(n))-cen_fit(2))^2+(col(coor_temp(n))-cen_fit(1))^2)/ratio;
                if dist(coor_temp(n)) < (dia_ave+5)/ratio
                    angle1(coor_temp(n)) = 0;
                    dist(coor_temp(n)) = 0;
                end
            end
        else             
            for n = 1:k
                tan_temp(n) = (row_temp(n)-cen_fit(2))/(col_temp(n)-cen_fit(1));
                if row_temp(n) <= cen_fit(2)
                    angle_temp(n) = atan(tan_temp(n))/pi*180+360;
                else
                    angle_temp(n) = atan(tan_temp(n))/pi*180;
                end
                angle1(coor_temp(n)) = angle_temp(n);
                dist(coor_temp(n)) = sqrt((row(coor_temp(n))-cen_fit(2))^2+(col(coor_temp(n))-cen_fit(1))^2)/ratio;
                if dist(coor_temp(n)) < (dia_ave+5)/ratio
                    angle1(coor_temp(n)) = 0;
                    dist(coor_temp(n)) = 0;
                end
            end            
        end
        i = i+1;        
    end
    
    A1=[angle1;dist];
    A2=[angle1;row'];
    A3=[angle1;col'];
    [Y,I]=sort(A1(1,:));
    B1=A1(:,I);
    B2=A2(:,I);
    B3=A3(:,I);
    
    savdir1 = 'C:\Users\slee\Documents\MATLAB\data of green particles\0.635mm 125particle\test\data points';
    fname = sprintf('finger_%i.mat',z);
    save(fullfile(savdir1,fname),'B1','B2','B3','cen_fit','radius_fit','ratio')
        
    close(figure(1))
    h=figure(1);
    set(h,'PaperPositionMode','auto')
    clf
    
    imshow(imgcrop);
    set(gcf,'PaperUnits','inches','PaperPosition',[0 0 x_pos y_pos])
    fname = sprintf('finger_%i.png',z);
    savdir2 = 'C:\Users\slee\Documents\MATLAB\data of green particles\0.635mm 125particle\test\pics2';
    fullfileName=fullfile(savdir2,fname);
    print('-dpng',fullfileName,'-r100');
    
    hold on
    plot(col,row,'b*','markersize',3)
    hold on
    ang = 0:0.01:2*pi;
    xp = radius_fit*cos(ang)+cen_fit(1);
    yp = radius_fit*sin(ang)+cen_fit(2);
    plot(xp,yp,'r-','markersize',3)
    
    
    set(gcf,'PaperUnits','inches','PaperPosition',[0 0 x_pos y_pos])
    fname = sprintf('finger_%i.png',z);
    savdir2 = 'C:\Users\slee\Documents\MATLAB\data of green particles\0.635mm 125particle\test\pics';
    fullfileName=fullfile(savdir2,fname);
    print('-dpng',fullfileName,'-r100');
    hold off
    
    count = count+1;
end
count
%% plot the growth trend of distance
% close all
% figure
% axis;
% xlabel('angle')
% ylabel('distance')
% step = floor(count/60);
% for k = 1:step
%     savdir = 'C:\Users\slee\Documents\MATLAB\data of green particles\1.15mm series one\100vis_150_20%_2\data points';
%     fname = sprintf('finger_%i.mat',60*k);
%     fig = load(fullfile(savdir,fname)); 
%     plot(fig.B1(1,:),fig.B1(2,:),'b.','markersize',5);
%     hold on
% end



