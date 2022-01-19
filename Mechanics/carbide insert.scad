//Turning Insert Identification code
//CCMT060204 
//C - 80deg diamond shape
//c - relief angle 7deg
//m - tolerance +/-.002
//06 - cutting edge length 6.35mm or 1/4"
//02 - insert thickness 2.38mm
//04 - nose,edge radius 0.4mm
//hole is either a #3-48 or M2.5x0.45, which are roughly equivelent 2.5146mm vs 2.5mm

//square

difference(){
 linear_extrude(height = 2.38, center = true, convexity = 10, scale=(6.35-2.35*tan(7))/6.35, slices = 5, $fn = 100)
 translate([2.35*tan(7), 0, 0])
    minkowski(){
        //difference(){
            square(size = 6.35-0.4, center = true);
            //circle(r=2.15/2);
        //}
        circle(r=0.4);
    }
    translate([2.35*tan(7), 0, 0])
    cylinder(r1 = 2.15/2,r2=3.52/2,h=2.4,center=true, $fn = 100);
}
