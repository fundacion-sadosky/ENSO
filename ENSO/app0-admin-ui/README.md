# App0 Admin Vue3 UI

## Getting started

The product uses:

- [`vue3`](https://github.com/vuejs/vue-next) Composition API
- Lightning-fast [`vitejs`](https://github.com/vitejs/vite) build & development tool
- [`Typescript`](https://github.com/microsoft/typescript) out of the box, for large-scale JavaScript applications for any browser
- Latest [`bulma`](https://bulma.io/) integration with `sass`
- Production ready `docker` images based on [bitnami](https://bitnami.com/)
- `npm` support
- `eslint`, `stylelint` and `prettier` pre-configured

### Prerequisites

- `VSCode` installed
- `Nodejs` 14.x with npm >7 installed
- `Typescript` 4.x installed
- `nvm` is an optional tool to manage local nodejs installations `https://github.com/nvm-sh/nvm`

### Dependencies installation

```bash
rm -rf node_modules
npm install --legacy-peer-deps
```

### Run a development server

```bash
npm run dev
```

### Keep it clean with linters

```bash
npm run test
```

```bash
npm run lint
```

### Build for production & run in preview mode

```bash
npm run build
npm run preview
```

### Using docker

```bash
make build-docker
```
