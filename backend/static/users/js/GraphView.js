
/*
参考サイト
https://api.anychart.com/v8/anychart
*/

//youtube読み込み
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);


var flag=-1;
var cont=document.getElementById('GraphView');
var stage = acgraph.create('GraphView');
var areaStage=stage.layer();
var lineDrawStage= stage.layer();

//グラフエリア描画
var rectangle = areaStage.rect(0,0,1000,350)
rectangle.fill({
        color: '#2196F3',
        opacity: 0.5
});
rectangle.parent(areaStage);

/*時間軸設定*/
function onPlayerReady(event) {
        //時間取得
        var time=event.target.getDuration();
        TimeText(time);
        //時間軸表示
}

//曲線描画
var linePath=lineDrawStage.path();
linePath.stroke('2 #000000');
var Point=[[0,350]];
linePath.parent(lineDrawStage);
cont.addEventListener('mousedown',function(){
        if(flag===-1){
                linePath.moveTo(0,350);
        }else{
                console.log(Point[Point.length-1]);
                linePath.moveTo(Point[Point.length-1][0],Point[Point.length-1][1]);
        }
        flag=1;
});
cont.addEventListener('click',function(){
        if(flag===-1){
                linePath.moveTo(0,0);
        }else{
                linePath.moveTo(Point[Point.length-1][0],Point[Point.length-1][1]);
        }
        cont.addEventListener('click',LineDraw);
});
cont.addEventListener('mousemove',function(){
        if(flag===1){
                cont.addEventListener('mousemove',LineDraw);             
        }
});
cont.addEventListener('mouseup',function(){
        flag=0;
        cont.removeEventListener('mousemove',LineDraw);
});

//時間テキスト描画
function TimeText(time){
        var timeArray=[0];
        var displayCount=(Math.floor(time/10))+1;
        var newTime=0;
        console.log(newTime);
        while(newTime<time){
                if((newTime+10)<time){
                        newTime=newTime+10;
                }else{
                        newTime=time;
                }
                timeArray.push(newTime);
                console.log(timeArray);
        }
        
        
}
//描画関数
function LineDraw(e){
        var x=e.pageX - GraphView.offsetLeft;
        var y=e.pageY - GraphView.offsetTop;
        if(y<350){
                linePath.lineTo(x,y);
                Point.push([x,y]);        
        }
}

