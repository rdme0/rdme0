# Glass skill icons

These are custom, static glass-style treatments of the profile's technology
marks. Each transparent PNG contains a glass tile and its caption. Separate
light and dark variants are selected with the README's `picture` elements.

Regenerate from the saved sources:

```sh
python scripts/render_skills.py --write-readme --browser-channel chrome
```

Omit `--browser-channel chrome` to use Playwright's installed Chromium.
Add `--fetch` only when intentionally updating the upstream logo geometry.

## Sources

- Most brand marks: [Simple Icons](https://github.com/simple-icons/simple-icons),
  CC0-1.0. Original SVGs and the license are saved in `source/`.
- Java, AWS, and gRPC marks:
  [Devicon](https://github.com/devicons/devicon), MIT. The license is saved in
  `source/devicon-MIT.txt`.
- JPA uses a custom letter mark. WebSocket and HTTP/SSE use custom protocol
  symbols. These are visual labels, not official product logos.
- Kotlin Coroutines reuses the Kotlin mark with an orbit. The three AWS
  services share the AWS wordmark and use different material tints.

The tile, highlights, gradients, and caption layout are original SVG artwork.
No live CSS blur or external icon service is required to display the README.
