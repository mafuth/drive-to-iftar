// Encode spaces in paths for better compatibility
function p(path: string) {
    return path.replace(/ /g, '%20');
}

export const ASSETS = {
    player: p('/kenney_car-kit/Models/GLB format/sedan-sports.glb'),
    road: {
        straight: p('/kenney_city-kit-roads/Models/GLB format/road-straight.glb'),
        ground: p('/kenney_city-kit-roads/Models/GLB format/tile-low.glb'), // Base ground
        groundNature: p('/kenney_nature-kit/Models/GLTF format/ground_grass.glb'), // Nature grounds
        light: p('/kenney_city-kit-roads/Models/GLB format/light-curved.glb')
    },
    obstacles: [
        p('/kenney_car-kit/Models/GLB format/taxi.glb'),
        p('/kenney_car-kit/Models/GLB format/truck.glb'),
        p('/kenney_car-kit/Models/GLB format/police.glb'),
        p('/kenney_car-kit/Models/GLB format/garbage-truck.glb'),
        p('/kenney_car-kit/Models/GLB format/delivery.glb'),
        p('/kenney_car-kit/Models/GLB format/ambulance.glb')
    ],
    collectibles: {
        watermelon: p('/kenney_food-kit/Models/GLB format/watermelon.glb'),
        date: p('/kenney_food-kit/Models/GLB format/avocado.glb')
    },
    zones: {
        city: [
            p('/kenney_city-kit-commercial_2.1/Models/GLB_format/building-a.glb'),
            p('/kenney_city-kit-commercial_2.1/Models/GLB_format/building-b.glb'),
            p('/kenney_city-kit-commercial_2.1/Models/GLB_format/building-c.glb'),
            p('/kenney_city-kit-commercial_2.1/Models/GLB_format/building-d.glb'),
            p('/kenney_city-kit-commercial_2.1/Models/GLB_format/building-skyscraper-a.glb'),
            p('/kenney_city-kit-commercial_2.1/Models/GLB_format/building-skyscraper-b.glb')
        ],
        suburbs: [
            p('/kenney_city-kit-suburban_20/Models/GLB format/building-type-a.glb'),
            p('/kenney_city-kit-suburban_20/Models/GLB format/building-type-b.glb'),
            p('/kenney_city-kit-suburban_20/Models/GLB format/building-type-c.glb'),
            p('/kenney_city-kit-suburban_20/Models/GLB format/building-type-d.glb'),
            p('/kenney_city-kit-suburban_20/Models/GLB format/building-type-e.glb')
        ],
        industrial: [
            p('/kenney_city-kit-industrial_1.0/Models/GLB format/building-a.glb'),
            p('/kenney_city-kit-industrial_1.0/Models/GLB format/building-b.glb'),
            p('/kenney_city-kit-industrial_1.0/Models/GLB format/building-c.glb'),
            p('/kenney_city-kit-industrial_1.0/Models/GLB format/building-d.glb'),
            p('/kenney_city-kit-industrial_1.0/Models/GLB format/building-e.glb')
        ],
        nature: [ // Maldives Theme: Trees & Flowers only
            p('/kenney_nature-kit/Models/GLTF format/tree_palm.glb'),
            p('/kenney_nature-kit/Models/GLTF format/tree_palmTall.glb'),
            p('/kenney_nature-kit/Models/GLTF format/tree_palmBend.glb'),
            p('/kenney_nature-kit/Models/GLTF format/tree_palmShort.glb'),
            p('/kenney_nature-kit/Models/GLTF format/tree_default.glb'),
            p('/kenney_nature-kit/Models/GLTF format/tree_oak.glb')
        ],
        bridge: [
            p('/kenney_watercraft-pack/Models/GLB format/boat-speed-a.glb'),
            p('/kenney_watercraft-pack/Models/GLB format/boat-speed-b.glb'),
            p('/kenney_watercraft-pack/Models/GLB format/boat-speed-c.glb'),
            p('/kenney_watercraft-pack/Models/GLB format/boat-fishing-small.glb'),
            p('/kenney_watercraft-pack/Models/GLB format/boat-fan.glb')
        ]
    },
    decorations: [
        p('/kenney_city-kit-roads/Models/GLB format/sign-highway.glb'),
        p('/kenney_city-kit-roads/Models/GLB format/construction-barrier.glb')
    ],
    characters: [
        p('/kenney_mini-characters/Models/GLB format/character-male-a.glb'),
        p('/kenney_mini-characters/Models/GLB format/character-female-a.glb'),
        p('/kenney_mini-characters/Models/GLB format/character-male-b.glb'),
        p('/kenney_mini-characters/Models/GLB format/character-female-b.glb')
    ],
    debris: [
        p('/kenney_car-kit/Models/GLB format/debris-tire.glb'),
        p('/kenney_car-kit/Models/GLB format/debris-bumper.glb'),
        p('/kenney_car-kit/Models/GLB format/cone.glb')
    ],
    cars: [
        p('/kenney_car-kit/Models/GLB format/sedan-sports.glb'),
        p('/kenney_car-kit/Models/GLB format/hatchback-sports.glb'),
        p('/kenney_car-kit/Models/GLB format/race-future.glb'),
        p('/kenney_car-kit/Models/GLB format/taxi.glb'),
        p('/kenney_car-kit/Models/GLB format/police.glb')
    ],
    traffic: {
        city: [
            p('/kenney_car-kit/Models/GLB format/taxi.glb'),
            p('/kenney_car-kit/Models/GLB format/police.glb'),
            p('/kenney_car-kit/Models/GLB format/ambulance.glb'),
            p('/kenney_car-kit/Models/GLB format/garbage-truck.glb'),
            p('/kenney_car-kit/Models/GLB format/delivery.glb'),
            p('/kenney_car-kit/Models/GLB format/sedan.glb')
        ],
        suburbs: [
            p('/kenney_car-kit/Models/GLB format/sedan.glb'),
            p('/kenney_car-kit/Models/GLB format/suv.glb'),
            p('/kenney_car-kit/Models/GLB format/van.glb'),
            p('/kenney_car-kit/Models/GLB format/delivery.glb'),
            p('/kenney_car-kit/Models/GLB format/police.glb'),
            p('/kenney_car-kit/Models/GLB format/ambulance.glb')
        ],
        industrial: [
            p('/kenney_car-kit/Models/GLB format/truck.glb'), // Using truck from obstacles
            p('/kenney_car-kit/Models/GLB format/delivery.glb'),
            p('/kenney_car-kit/Models/GLB format/van.glb'),
            p('/kenney_car-kit/Models/GLB format/garbage-truck.glb')
        ],
        nature: [
            p('/kenney_car-kit/Models/GLB format/suv.glb'),
            p('/kenney_car-kit/Models/GLB format/van.glb'),
            p('/kenney_car-kit/Models/GLB format/sedan.glb') // Tourists?
        ]
    },
    ui: {
        watermelon: p('/kenney_food-kit/Previews/watermelon.png'),
        coconut: p('/kenney_food-kit/Previews/coconut.png'),
        soda: p('/kenney_food-kit/Previews/soda.png')
    },
    music: [
        p('/music/track_1.mp3'),
        p('/music/track_2.mp3')
    ],
    sounds: {
        horn: p('/sounds/horn.mp3')
    }
};

// Flatten ASSETS for preloading
export const ALL_ASSETS: string[] = (() => {
    const urls: string[] = [];
    const traverse = (obj: any) => {
        for (const key in obj) {
            if (typeof obj[key] === 'string') {
                urls.push(obj[key]);
            } else if (Array.isArray(obj[key])) {
                obj[key].forEach((item: any) => {
                    if (typeof item === 'string') urls.push(item);
                    else traverse(item);
                });
            } else if (typeof obj[key] === 'object') {
                traverse(obj[key]);
            }
        }
    };
    traverse(ASSETS);
    return [...new Set(urls)]; // Deduplicate
})();
