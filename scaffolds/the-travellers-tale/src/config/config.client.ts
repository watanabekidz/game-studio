import { provideClientGlobalConfig, provideClientModules, Presets } from "@rpgjs/client";
import { provideMain } from "../modules/main";
import { provideTiledMap } from "@rpgjs/tiledmap/client";

export default {
  providers: [
    provideTiledMap({
      basePath: "map",
    }),
    provideClientGlobalConfig(),
    provideMain(),
    provideClientModules([
      {
        spritesheets: [
          {
            id: 'hero',
            image: 'spritesheets/hero.png',
            ...Presets.RMSpritesheet(3, 4)
          },
          {
            id: 'female',
            image: 'spritesheets/female.png',
             ...Presets.RMSpritesheet(3, 4)
          },
          {
            id: 'male',
            image: 'spritesheets/male.png',
             ...Presets.RMSpritesheet(3, 4)
          },
          // Pipoya character sprites
          {
            id: 'innkeeper',
            image: 'spritesheets/innkeeper.png',
            ...Presets.RMSpritesheet(3, 4)
          },
          {
            id: 'patron',
            image: 'spritesheets/patron.png',
            ...Presets.RMSpritesheet(3, 4)
          },
          {
            id: 'wanderer',
            image: 'spritesheets/wanderer.png',
            ...Presets.RMSpritesheet(3, 4)
          },
          {
            id: 'guard',
            image: 'spritesheets/guard.png',
            ...Presets.RMSpritesheet(3, 4)
          },
          {
            id: 'female-01',
            image: 'spritesheets/female-01.png',
            ...Presets.RMSpritesheet(3, 4)
          },
          {
            id: 'male-01',
            image: 'spritesheets/male-01.png',
            ...Presets.RMSpritesheet(3, 4)
          }
        ]
      }
    ])
  ],
};
