
let canvas = null; 
let context = null;
let time = 0;
const Point = class {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
    equals(point) {
        return this.x === point.x && this.y === point.y;
    }
    toString() {
        return '(' + this.x + ', ' + this.y + ')';
    }

};

const FourierCircle = class {
    constructor(speed, radius, initial_angle)
    {
        this.radius = radius/2;
        this.speed = speed/20;
        this.initial_angle = initial_angle
    }
    draw(ctx, at) 
    {
        ctx.beginPath();
        //ctx.arc(at.x, at.y, this.radius, 0, Math.PI * 2, true);
        var x = at.x + this.radius * Math.cos(this.initial_angle + 2 * Math.PI * time * this.speed);
        var y = at.y + this.radius * Math.sin(this.initial_angle + 2 * Math.PI * time * this.speed);
        ctx.moveTo(at.x, at.y);
        ctx.lineTo(x, y);
        ctx.closePath();
        ctx.strokeStyle = 'rgba(202, 126, 86, 0.7)';
        ctx.lineWidth = 1; 
        ctx.stroke();
    }

    nextCenter(at) 
    {
        var x = at.x + this.radius * Math.cos(this.initial_angle + 2 * Math.PI * time * this.speed);
        var y = at.y + this.radius * Math.sin(this.initial_angle + 2 * Math.PI * time * this.speed);
        return new Point(x, y)
    }
};

let n;
let circles;
let animation_id = 0;
let center = new Point(150, 150);
let wave = [];
let nr_of_paths;
let flag = false;
function init_fourier(canvas_elm, constants, count) {
    canvas = canvas_elm;
    context = canvas.getContext('2d');
    context.beginPath();
    context.fillStyle = "rgba(255, 255, 255, 255)";
    context.fillRect(0, 0, canvas.width, canvas.height);    
    context.stroke();
    if(flag==false){
        context.transform(1, 0, 0, -1, 0, canvas.height);
        flag=true;
    }

    if(animation_id !== 0)
        window.cancelAnimationFrame(animation_id);
    n = count;

    circles = [];
    nr_of_paths = constants.length/((count-1)*2+1);
    for(let i=0;i<nr_of_paths;i++){
        wave.push([]);
    } 
    //console.log("lenght const"+ constants.length)

    for (let i = 0; i < constants.length; i++) {
        let constant = constants[i];
        circles[i] = new FourierCircle(constant.s, constant.r, constant.a);
    }
    animation_id = window.requestAnimationFrame(draw);
}

function draw_wave(ctx,wave,j) {
    // ctx.beginPath();
    for (let i = 1; i < wave[j].length; i++) {
        ctx.beginPath();
        ctx.moveTo(wave[j][i-1].x, wave[j][i-1].y);
        ctx.lineTo(wave[j][i].x, wave[j][i].y);
        ctx.closePath();

        // let c = Math.ceil(127.0 + 128.0*i/wave.length);
        let alpha = 1 - i*1.0/wave[j].length;
        
        ctx.strokeStyle = 'rgba(0, 0, 0, ' + alpha + ')';
        //ctx.strokeStyle = 'rgba(0, 0, 0, 1)';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
    // ctx.closePath();
    // ctx.strokeStyle = 'rgba(0, 0, 0, 1)';
    // ctx.stroke();
} 

// function draw_wave2(ctx) {
//     // ctx.beginPath();
//     for (let i = 1; i < wave2.length; i++) {
//         ctx.beginPath();
//         ctx.moveTo(wave2[i-1].x, wave2[i-1].y);
//         ctx.lineTo(wave2[i].x, wave2[i].y);
//         ctx.closePath();

//         // let c = Math.ceil(127.0 + 128.0*i/wave.length);
//         let alpha = 1 - i*1.0/wave2.length;
        
//         ctx.strokeStyle = 'rgba(0, 0, 0, ' + alpha + ')';
//         //ctx.strokeStyle = 'rgba(0, 0, 0, 1)';
//         ctx.lineWidth = 1;
//         ctx.stroke();
//     }
//     // ctx.closePath();
//     // ctx.strokeStyle = 'rgba(0, 0, 0, 1)';
//     // ctx.stroke();
// } 


function draw() {
    console.log("ia tut ne bil");
    context.clearRect(0,0, canvas.width, canvas.height);
    // let new_center = center;
    let count;


    for(let j=0;j<nr_of_paths;j++){
        count = 2*n*j-1*j;
        if(j==0)count=0;
        //console.log("count for "+j+" count = "+count)
        //console.log(nr_of_paths)
        var new_center = circles[count].nextCenter(center);
        for(let i = 1; i < n; i++) {
            circles[i+count].draw(context, new_center);
         new_center = circles[i+count].nextCenter(new_center);
        }
          draw_wave(context,wave,j);
          wave[j].unshift(new_center);

          if(wave[j].length > 500) {
            wave[j].pop();
        }
    }




    


    // var new_center = circles[201].nextCenter(center);
    // for(let i = 1; i < n; i++) {
    //     circles[i+201].draw(context, new_center);
    //     new_center = circles[i+201].nextCenter(new_center);
    // }
    //   draw_wave(context,wave2);
    //   wave2.unshift(new_center);


    //   console.log(wave);
    //   console.log(wave2.length);
        
        
    
    

    animation_id = window.requestAnimationFrame(draw);

    time += 0.04;
    
}
