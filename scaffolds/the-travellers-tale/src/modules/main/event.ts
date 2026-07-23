import { type EventDefinition, RpgPlayer } from '@rpgjs/server'

export interface Topic {
    id: string
    ask: string
    response: string
    followUp?: string
}

export interface NpcDialog {
    name: string
    greeting: string
    pokes: string[]
    topics: Topic[]
}

const stateMap = new WeakMap<object, { pokeIndex: number }>()

export function TavernNpc(graphic: string, dialog: NpcDialog): EventDefinition {
    return {
        onInit() {
            this.setGraphic(graphic)
            stateMap.set(this, { pokeIndex: 0 })
        },
        async onAction(player: RpgPlayer) {
            let state = stateMap.get(this)
            if (!state) {
                state = { pokeIndex: 0 }
                stateMap.set(this, state)
            }
            const opts = { speaker: dialog.name, talkWith: this }
            const msg = state.pokeIndex === 0 ? dialog.greeting : dialog.pokes[state.pokeIndex % dialog.pokes.length]
            state.pokeIndex++

            await player.showText(msg, opts)
            let talking = true
            while (talking) {
                const choices = dialog.topics.map(t => ({ text: t.ask, value: t.id }))
                choices.push({ text: 'Goodbye', value: 'goodbye' })
                const choice = await player.showChoices('Ask about:', choices, opts)
                if (!choice || choice.value === 'goodbye') {
                    talking = false
                } else {
                    const topic = dialog.topics.find(t => t.id === choice.value)
                    if (topic) {
                        await player.showText(topic.response, opts)
                        if (topic.followUp) {
                            await player.showText(topic.followUp, opts)
                        }
                    }
                }
            }
        }
    }
}
