import { defineModule } from "@rpgjs/common";
import { RpgServer } from "@rpgjs/server";
import { player } from './player'
import { TavernNpc } from "./event";
import innkeeperDialog from './npc-dialog/innkeeper.json'
import patronDialog from './npc-dialog/patron.json'
import wandererDialog from './npc-dialog/wanderer.json'

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
                    x: 480,
                    y: 256,
                    event: TavernNpc('male', innkeeperDialog)
                },
                {
                    id: 'patron',
                    x: 192,
                    y: 416,
                    event: TavernNpc('female', patronDialog)
                },
                {
                    id: 'wanderer',
                    x: 640,
                    y: 160,
                    event: TavernNpc('male', wandererDialog)
                }
            ]
        }
    ]
});
