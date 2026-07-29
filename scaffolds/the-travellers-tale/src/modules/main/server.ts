import { defineModule } from "@rpgjs/common";
import { RpgServer } from "@rpgjs/server";
import { player } from './player'
import { TavernNpc } from "./event";
import innkeeperDialog from './npc-dialog/innkeeper.json'
import patronDialog from './npc-dialog/patron.json'
import wandererDialog from './npc-dialog/wanderer.json'
import guardDialog from './npc-dialog/guard.json'
import cookDialog from './npc-dialog/cook.json'

export default defineModule<RpgServer>({
    player,
    maps: [
        {
            id: 'simplemap',
            events: [{
                id: 'npc',
                x: 300,
                y: 400,
                event: TavernNpc('female', innkeeperDialog)
            }]
        },
        {
            id: 'tavern',
            events: [
                {
                    id: 'innkeeper',
                    x: 192,
                    y: 224,
                    event: TavernNpc('innkeeper', innkeeperDialog)
                },
                {
                    id: 'patron',
                    x: 384,
                    y: 320,
                    event: TavernNpc('patron', patronDialog)
                },
                {
                    id: 'wanderer',
                    x: 672,
                    y: 320,
                    event: TavernNpc('wanderer', wandererDialog)
                },
                {
                    id: 'guard',
                    x: 64,
                    y: 128,
                    event: TavernNpc('guard', guardDialog)
                },
                {
                    id: 'cook',
                    x: 736,
                    y: 128,
                    event: TavernNpc('female-01', cookDialog)
                }
            ]
        }
    ]
});
