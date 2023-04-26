# Open-Shredder
OpenShredder is a general purpose 3D printable shredder designed for recycling plastic


The goal of this project is to democratize the knowledge and empower individuals to remove plastics from their community waste stream and transform them through the below described processes into long lived, durable goods that can again be recycled at the end of their usefulness. 

# Scope of Work

Initially, non-uniform plastic objects need to be mechanically broken down into a uniform format that can be processed into new products. This first process requires a shredder, which is a machine that mechanically breaks plastic down into uniform pieces of a desired size.

The shredder needs to be relatively quiet and be able to handle the recyclable plastic seen in modern society. 

| Recycle #1 | PET | polyethylene terephthalate |
| Recycle #2 | HDPE | polyethylene, high density |
| Recycle #3 | PVC | poly(vinyl chloride) |
| Recycle #4 | LDPE | polyethylene, low density |
| Recycle #5 | PP | polypropylene |


Plastics can have fillers, contamination, or be damaged from UV, thermal, or mechanical stress that change their initial properties. In these cases, mixing in additive plastics can help mitigate the damage and restore some of the materials initial properties. Additive plastics can be freshly manufactured plastic or plastics with complementary properties. We're investigating if https://docs.plasticscanner.com/ can be used to fill this need.

On the market, there are several commercial shredder options designed for dedicated spaces and high volume plastic shredding. Unfortunately, these machines and techniques do not meet the above goal of being usable by a single individual. A cooperative community recycling center would be ideal for one of these high volume machines.

The best documented and supported DIY plastic shredder would be the Precious Plastics Shredder. However, the current bill of materials (BOM) lists the price as $2,234.17, which is an amazing 5x lower price difference from commercial shredders and is competitive with equivalent commercial shredders from Asian markets. This doesn’t include labor and overhead plus reinvestment profits. 

# Objective

To realize a further reduction of price and complexity, a shredder designed from the ground up to be sustainable and accessible needs to be developed. By designing mechanical components capable of being made on a 3D printer, we potentially can use the very plastic material shredded in the creation of new shredders, as well as expand the list of useful machines buildable with a 3D printer. When considering a shredder built of plastic designed to shred plastic, we will both need to create a community, collaborate with an existing community, or reinvigorate an inactive community as it is unlikely that our initial efforts will be sufficient to solve low cost waste processing. Community activity can’t only be limited to technical work. Cultural and social norms around recycling need to be addressed and both trust and accountability need to be earned. We can leverage an Open Source Hardware project and a call to action, along with organizational resources such as documentation management, official builds, development resources, and coordination of efforts. 

Currently the design of the shredder is thought to be a single shaft shredder, which is a simple but robust design that uses a pusher lever to feed material against rotating knives along a single stationary blade. A screen acts as a filter to only let material of a certain shape through. These machines use low speed, high torque gearboxes to process a high variety of materials. 

To accomplish this with a 3D printed shredder, it is envisioned that the central shaft will be 3D printed and like with commercial units, steel or carbide inserts will make up the cutting knife edges, and plastic will provide backing and support. To provide high torque, a cycloidal gearbox will be coupled to the shaft on both sides to provide support and the required force. 

Future work includes using the shredded material in a variety of applications, some of which are demonstrated by Precious Plastics, such as building materials and consumer goods. A further goal would be to use the shredded plastic for 3D printing as either feed stock for a filament extruder or directly with a pellet extruder 3D printing head. 

# Project Outline

## Tools Used
SPEC will develop an easily installable web hosted Jupyter notebook and docker container that has all the tools nessisary to contribute to this project. 

CadQuery is a parametric 3D Computer Aided Design (CAD) language and software library, written in Python, that allows for expressive 3D designs to be modeled and assembeled virtually. 

CadQuery: https://github.com/CadQuery/cadquery

Jupyter-CadQuery, combines the utility of Jupyter notebooks, with 3D cad drawings produced with CadQuery. It also allows for live code and deploy environments, and many more features. 

Jupiter-CadQuery: https://github.com/bernhard-42/jupyter-cadquery

## Proof of Concept

  The first proof of concept, will utilize a fully parametrized 3D printed shredder drum

## First Release

## Rolling Release Schedule

## Production and Manufacturing

# Cycloidal Generators:
https://github.com/RepRapLtd/RobotComponents/tree/main/RRL-cycloidal-drive
https://github.com/mawildoer/cycloidal_generator
https://github.com/mikedh/cycloidal
https://hackaday.io/project/168498-opencyre

## Related Projects
https://github.com/CubeFactory2/cubefactory
