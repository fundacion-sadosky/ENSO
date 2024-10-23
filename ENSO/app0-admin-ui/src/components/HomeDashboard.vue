<script setup lang="ts">
import { computed, ref, onBeforeMount } from 'vue'
import { useSession } from '/@src/stores/session'
import { useRouter } from 'vue-router'
import { useNotyf } from '/@src/composable/useNotyf'
import { platformService } from '/@src/services/platformService'
import { onceImageErrored } from '/@src/utils/via-placeholder'
import type { AppDef } from '/@src/models/platform'

const router = useRouter()
const session = useSession()
const notyf = useNotyf()

const apps = ref<AppDef[]>([])

const filteredApps = computed(() => {
  return apps.value
})

const goTo = (appUrl: any) => {
  if (appUrl.startsWith('http')) {
    window.location.href = appUrl
  } else {
    router.push(appUrl)
  }
}

const userDesc = computed(() => {
  if (session.isAdmin) {
    return 'Administrator of INGAR PUE Platform'
  }
  return 'User of INGAR PUE Platform'
})

const loadUserApps = async () => {
  try {
    apps.value = await platformService.getCurrUserApps()
    if (apps.value.length == 1) {
      // redirect to app
      if (apps.value[0].url) {
        goTo(apps.value[0].url)
      }
    }
  } catch (error: any) {
    notyf.error(error.message)
  }
}

onBeforeMount(async () => {
  await loadUserApps()
})
</script>

<template>
  <div class="personal-dashboard personal-dashboard-v2">
    <div class="columns is-multiline">
      <div class="column is-12">
        <div class="dashboard-header">
          <Logo :image="session.userData.image" :name1="session.userData.fullname" size="xl" />

          <div class="user-meta is-dark-bordered-12">
            <h3 class="title is-4 is-narrow is-bold">{{ session.userData.fullname }}</h3>
            <p class="light-text">{{ userDesc }}</p>
          </div>
          <div class="user-action">
            <h3 class="title is-2 is-narrow">INGAR PUE</h3>
            <p class="light-text">Aplicaciones de Productividad Avanzada</p>
          </div>
          <div class="cta h-hidden-tablet-p">
            <div class="media-flex inverted-text">
              <i aria-hidden="true" class="lnil lnil-world"></i>
              <p class="white-text">INGAR</p>
            </div>
            <a href="http://ingar.santafe-conicet.gov.ar" target="_blank" class="link inverted-text">Ver más</a>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div>
    <div class="card-grid card-grid-v2">
      <!--List Empty Search Placeholder -->
      <VPlaceholderPage
        :class="[filteredApps.length !== 0 && 'is-hidden']"
        title="We couldn't find any App for your."
        subtitle="Looks like we couldn't find any any App accesible."
        larger
      >
        <template #image>
          <img class="light-image" src="../assets/illustrations/placeholders/search-3.svg" alt="" />
          <img class="dark-image" src="../assets/illustrations/placeholders/search-3-dark.svg" alt="" />
        </template>
      </VPlaceholderPage>

      <!--Card Grid v2-->
      <transition-group name="list" tag="div" class="columns is-multiline">
        <!--Grid Item-->
        <div v-for="item in filteredApps" :key="item.id" class="column is-4">
          <div class="card-grid-item">
            <div class="card">
              <div class="card-image">
                <figure class="image is-16by9">
                  <img
                    v-if="item.image"
                    :src="platformService.getLogoURL(item.image)"
                    alt=""
                    @error.once="(event) => onceImageErrored(event, '1280x960')"
                  />
                  <img v-else src="" alt="" @error.once="(event) => onceImageErrored(event, '1280x960')" />
                </figure>
              </div>
              <div class="card-content">
                <div class="card-content-flex">
                  <div class="card-info">
                    <h3 class="dark-inverted">{{ item.name }}</h3>
                    <p class="dark-inverted">{{ item.description }}</p>
                  </div>
                </div>
              </div>
              <footer class="card-footer">
                <a href="#" class="card-footer-item" @click="goTo(item.url)">Ir a la APP</a>
              </footer>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<style lang="scss">
@import '/@src/scss/abstracts/all';

.is-navbar {
  .personal-dashboard {
    margin-top: 30px;
  }
}

.personal-dashboard-v2 {
  .dashboard-header {
    @include vuero-s-card;

    display: flex;
    align-items: center;
    padding: 30px;

    .user-meta {
      padding: 0 3rem;
      border-right: 1px solid var(--fade-grey-dark-3) h3 {
        max-width: 180px;
      }
    }

    .user-action {
      padding: 0 3rem;
    }

    .cta {
      position: relative;
      flex-grow: 2;
      max-width: 275px;
      margin-left: auto;
      background: var(--primary-light-8);
      padding: 20px;
      border-radius: var(--radius-large);
      box-shadow: var(--primary-box-shadow);

      .lnil,
      .lnir {
        position: absolute;
        bottom: 1rem;
        right: 1rem;
        font-size: 4rem;
        opacity: 0.3;
      }

      .link {
        font-family: var(--font-alt);
        display: block;
        font-weight: 500;
        margin-top: 0.5rem;

        &:hover,
        &:focus {
          color: var(--smoke-white);
          opacity: 0.6;
        }
      }
    }
  }

  .dashboard-card {
    @include vuero-s-card;

    padding: 30px;

    &:not(:last-child) {
      margin-bottom: 1.5rem;
    }

    .card-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;

      h3 {
        font-family: var(--font-alt);
        font-size: 1rem;
        font-weight: 600;
        color: var(--dark-text);
        margin-bottom: 0;
      }
    }

    .active-projects,
    .active-team,
    .active-list {
      padding: 10px 0;
    }
  }
}

.is-dark {
  .personal-dashboard-v2 {
    .dashboard-header,
    .dashboard-card {
      @include vuero-card--dark;
    }

    .home-header {
      .cta {
        background: var(--primary-light-2);
        box-shadow: var(--primary-box-shadow);
      }
    }
  }
}

@media only screen and (max-width: 767px) {
  .personal-dashboard-v2 {
    .dashboard-header {
      flex-direction: column;
      text-align: center;

      .v-avatar {
        margin-bottom: 10px;
      }

      .user-meta {
        padding-top: 10px;
        padding-bottom: 10px;
        border: none;
      }

      .user-action {
        padding-bottom: 30px;
      }

      .cta {
        margin-left: 0;
      }
    }

    .active-projects {
      .media-flex-center {
        .flex-end {
          .avatar-stack {
            display: none;
          }
        }
      }
    }
  }
}

.card-grid {
  .columns {
    margin-left: -0.5rem !important;
    margin-right: -0.5rem !important;
    margin-top: -0.5rem !important;
  }

  .column {
    padding: 0.5rem !important;
  }
}

.card-grid-v2 {
  .card-grid-item {
    .card {
      border: 1px solid var(--fade-grey-dark-4);
      box-shadow: none;
      border-radius: var(--radius-large);

      .card-header {
        box-shadow: none;
        border-bottom: 1px solid var(--fade-grey-dark-4);

        .card-header-title {
          display: flex;
          align-items: center;

          .meta {
            margin-left: 10px;
            line-height: 1.2;

            span {
              display: block;
              font-weight: 400;

              &:first-child {
                font-family: var(--font-alt);
                font-size: 0.95rem;
                color: var(--dark-text);
                font-weight: 600;
              }

              &:nth-child(2) {
                font-size: 0.9rem;
                color: var(--light-text);
              }
            }
          }
        }
      }

      .card-image {
        img {
          object-fit: cover;
        }
      }

      .card-content {
        border-top: 1px solid var(--fade-grey-dark-4);
        padding: 1rem;

        .card-content-flex {
          display: flex;
          align-items: center;
          justify-content: space-between;

          .card-info {
            h3 {
              font-family: var(--font-alt);
              font-size: 1rem;
              color: var(--dark-text);
              font-weight: 600;
            }

            p {
              font-size: 0.9rem;

              svg {
                position: relative;
                top: 0;
                height: 14px;
                width: 14px;
                margin-right: 4px;
              }
            }
          }
        }
      }

      .card-footer {
        a {
          font-family: var(--font);
          color: var(--light-text);
          padding: 1rem 0.75rem;
          transition: all 0.3s; // transition-all test

          &:hover {
            background: var(--fade-grey-light-4);
            color: var(--primary);
          }
        }
      }
    }
  }
}

.is-dark {
  .card-grid-v2 {
    .card-grid-item {
      border-color: var(--dark-sidebar-light-12);

      .card {
        background: var(--dark-sidebar-light-6);
        border-color: var(--dark-sidebar-light-12);

        .card-header {
          border-color: var(--dark-sidebar-light-12);
        }

        .card-content {
          border-color: var(--dark-sidebar-light-12);

          .avatar-stack {
            .avatar {
              border-color: var(--dark-sidebar-light-6);
            }
          }
        }

        .card-footer {
          border-color: var(--dark-sidebar-light-12);

          a {
            border-color: var(--dark-sidebar-light-12);

            &:hover,
            &:focus {
              background: var(--dark-sidebar-light-2);
              color: var(--primary);
            }
          }
        }
      }
    }
  }
}
</style>
