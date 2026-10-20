# cr8-plugins

LinkedIn Ads plugins by Bogdan Liutic, CR8 (cr8.eco). There's one plugin in this repo, `signal-loop`. It's four read-only checks for LinkedIn Ads on a signal list. A signal list is the companies that fit your buyer, sorted by a dated, public reason to buy now. It also carries the scenario "Warm leads from a signal list" from The AI Standard: LinkedIn Ads.

## Add it

In Claude Code:

```
/plugin marketplace add bogdanl-rgb/cr8-plugins
/plugin install signal-loop@cr8
```

From a shell it's one line: `claude plugin install signal-loop --marketplace bogdanl-rgb/cr8-plugins`.

In Cowork, download `signal-loop.plugin` from this repo's Releases page and upload it as a plugin.

Want to try it in Claude Code without installing? Download `signal-loop-1.0.0.zip` from the same page and start Claude Code with `claude --plugin-dir signal-loop-1.0.0.zip`.

In claude.ai, zip each skill folder in `signal-loop/skills/` and upload it as a skill.

I'd start with `signal-loop/README.md`, then the sample files in `signal-loop/examples/`.

## License

The text is CC BY 4.0, so anyone can reuse it with credit: "Bogdan Liutic, CR8 (cr8.eco)". Scripts and manifests are MIT. DemandSense may publish, package and edit this plugin for The AI Standard under the names signal-loop and Signal Loop, with my credit, once I've seen the final version. The two images on the Standard's pages are © CR8 and aren't in this repo. See LICENSE.

Built by Bogdan Liutic, CR8 (cr8.eco). Want the loop run for you? [cr8.eco](https://cr8.eco/?utm_source=signal-loop-plugin)
