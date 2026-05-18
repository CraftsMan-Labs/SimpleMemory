/**
 * Tiptap node + InputRule that recognise `[[Wiki Page]]` and render them as
 * clickable inline tokens. Persists round-trip with Markdown via tiptap-markdown.
 *
 * Autocomplete is driven by Suggestion which calls our `/v1/wiki/pages?q=` endpoint.
 */
import { Node, mergeAttributes, InputRule, type CommandProps } from '@tiptap/core'
import Suggestion, { type SuggestionOptions } from '@tiptap/suggestion'
import type { WikiPage } from '@@/types/api'

export interface WikiLinkAttrs {
  slug: string
  title: string
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    wikiLink: {
      insertWikiLink: (attrs: WikiLinkAttrs) => ReturnType
    }
  }
}

export interface WikiLinkOptions {
  HTMLAttributes: Record<string, string>
  onClick: (attrs: WikiLinkAttrs) => void
  suggestionRender: SuggestionOptions['render']
  fetchPages: (q: string) => Promise<WikiPage[]>
}

export const WikiLink = Node.create<WikiLinkOptions>({
  name: 'wikiLink',
  inline: true,
  group: 'inline',
  atom: true,
  selectable: true,

  addOptions() {
    return {
      HTMLAttributes: { class: 'wikilink' },
      onClick: () => {},
      suggestionRender: () => ({ onStart: () => {}, onUpdate: () => {}, onKeyDown: () => false, onExit: () => {} }),
      fetchPages: async () => [],
    }
  },

  addAttributes() {
    return {
      slug: { default: '' },
      title: { default: '' },
    }
  },

  parseHTML() {
    return [{ tag: 'a[data-wikilink]' }]
  },

  renderHTML({ node, HTMLAttributes }) {
    return [
      'a',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-wikilink': 'true',
        'data-slug': node.attrs.slug,
        href: `#wiki:${node.attrs.slug}`,
      }),
      `[[${node.attrs.title}]]`,
    ]
  },

  addCommands() {
    return {
      insertWikiLink:
        (attrs: WikiLinkAttrs) =>
        ({ chain }: CommandProps) =>
          chain().insertContent({ type: this.name, attrs }).insertContent(' ').run(),
    }
  },

  addInputRules() {
    return [
      new InputRule({
        find: /\[\[([^\]]+)\]\]\s$/,
        handler: ({ state, range, match }) => {
          const raw = match[1]
          if (!raw) return
          const title = raw.trim()
          const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-')
          state.tr.replaceWith(range.from, range.to, this.type.create({ title, slug }))
        },
      }),
    ]
  },

  addProseMirrorPlugins() {
    return [
      Suggestion({
        editor: this.editor,
        char: '[[',
        startOfLine: false,
        allowSpaces: true,
        decorationTag: 'span',
        decorationClass: 'wikilink-suggestion',
        command: ({ editor, range, props }) => {
          const attrs = props as WikiLinkAttrs
          editor
            .chain()
            .focus()
            .deleteRange(range)
            .insertContent({ type: 'wikiLink', attrs })
            .insertContent(' ')
            .run()
        },
        items: async ({ query }) => {
          const pages = await this.options.fetchPages(query)
          return pages.map((p) => ({ title: p.title, slug: p.slug }))
        },
        render: this.options.suggestionRender,
      }),
    ]
  },
})
