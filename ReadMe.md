<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!-- [![Contributors][contributors-shield]][contributors-url] -->
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://www.djura.it" target="_blank" rel="noopener noreferrer">
    <img src="images/djura-logo.png" alt="Logo" width="250" >
  </a>

  <h3 align="center">Djura-Tools</h3>

  <p align="center">
    Helper functions and tools for Djura applications
    <br />
    <a href="https://github.com/djura-risk-data-engineering/djura-tools" target="_blank" rel="noopener noreferrer"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://apps.djura.it/" target="_blank" rel="noopener noreferrer">Try the Apps</a>
    ·
    <a href="https://github.com/djura-risk-data-engineering/djura-tools/issues/new?labels=bug&template=bug-report---.md" target="_blank" rel="noopener noreferrer">Report Bug</a>
    ·
    <a href="https://github.com/djura-risk-data-engineering/djura-tools/issues/new?labels=enhancement&template=feature-request---.md" target="_blank" rel="noopener noreferrer">Request Feature</a>
    ·
    <a href="https://www.djura.it/blog" target="_blank" rel="noopener noreferrer">Blog</a>
    ·
    <a href="https://www.youtube.com/@djura-risk-engineering-data/videos" target="_blank" rel="noopener noreferrer">Youtube</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About Djura - Risk-Data-Engineering</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#helper-tools">Helper Tools</a>
      <ul>
        <li><a href="#hazard">Hazard</a></li>
        <li><a href="#record-selector">Record-Selector</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#build-package">Build package</a></li>
        <li><a href="#testing">Testing</a></li>
      </ul>
    </li>
    <!-- <li><a href="#roadmap">Roadmap</a></li> -->
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About [Djura - Risk-Data-Engineering](https://www.djura.it/)

<!-- [![Djura Screen Shot][product-screenshot]](https://www.djura.it/) -->

Djura is a young, motivated team providing digital tools and engineering services to turn ideas into reality. We combine ongoing development and academic engagement with expert consulting to meet diverse industry needs. Our goal is to empower clients with the skills to navigate complex risks, fostering a safer and well-informed society.


What we do:
* We provide a cloud-based platform offering computational tools and digital services for catastrophe risk engineering
* We offer engineering consultation services for risk assessment and design, resource prioritisation and management and decision-making
* We offer online and in-person courses and support material to foster professional training and development

**Our mission** is to empower global resilience through innovative, user-friendly solutions in catastrophe risk modelling and engineering analysis, delivered with unparalleled expertise, diversity, and cost-effectiveness.

**Our vision** is a world where complex problems are effectively tackled with the right know-how. We believe in achieving this by equipping analysts and stakeholders with the necessary tools, expertise, and support to arrive at the optimal solution.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Helper Tools
Currently available functions.

### Hazard
- Preparing Hazard outputs for Record Selection
  - Processing the datastore
  - Processing the disaggregation results

### Record-Selector
- Preparation of Record Selection outputs at different intensity measure levels for hazard consistency checks


### Built With

This section showcases the key technologies, frameworks, and tools that power both our codebase and our [service](https://apps.djura.it) ecosystem. From the core architecture to the user-facing components, these technologies work together to deliver our products and services.

| Name             | Badge                                                                                                                                   | Description                                                                                                                                  |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Nuxt     | [![Nuxt][Nuxt.js]][Nuxt-url]             | Typescript Frontend Technology             |
| Flask     | [![Flask][Flask]][Flask-url]            | Python Backend Technology             |
| AWS-EC2     | [![AWS][AWS]][AWS-url]            | Backend Cloud Server             |
| Vercel     | [![Vercel][Vercel]][Vercel-url]            | Frontend Server             |
| AWS-S3     | [![S3][S3]][S3-url]            | Storage             |
| Supabase-S3     | [![Supabase][Supabase]][Supabase-url]            | Database Solution            |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

This section guides you through the necessary steps to begin using our tools and services.

**Website Access**

- Visit our website at [https://www.djura.it](https://www.djura.it) to access our full suite of tools.
- Guest Access allows you to explore and use our tools without creating an account.
- Navigate to the tools dashboard to browse available options.

**Data Preparation**

- Download this repository if you need to pre-process your data.
- This is a data preparation repository with useful functions for Djura applications.
- Use the necessary functions and scripts to format your data appropriately.

### Prerequisites

Python (recommended version 3.12) is required for using this repository. 

### Installation

1. Clone the repo
    ```sh
    git clone https://github.com/djura-risk-data-engineering/djura-tools.git
    ```
3. Create a virtual environment (recommended but optional)
    ```sh
    python -m venv venv
    venv\Scripts\activate   # (windows)
    source venv/bin/activate    # (mac)
    ```
4. Install python packages - approach 1 (recommended approach)
    ```sh
    venv\Scripts\activate
    pip install poetry

    # to install/update current pyproject.toml
    poetry install

    # to add a new package
    poetry add package_name

    # installing dev dependencies only
    poetry add pytest --group dev
    poetry install --with dev
    ```
5. Install python packages - approach 2
    ```sh
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Build package
This is optional

```shell
poetry build
pip install dist/djura_tools-**x.x.x**-py3-none-any.whl
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Testing
Example tests.

```shell
pytest --disable-warnings --verbose -rP
pytest tests/test_file.py::test_name --disable-warnings --verbose -rP -s
pytest tests/test_file.py -k test_name --disable-warnings --verbose -rP -s
pytest -s --durations=10 --durations-min=0.01
```

Tu run tests in parallel (4 processes)
```shell
pytest -n 4
pytest --ff -n 4    # (rerun only failed tests in parallel)
```

## License

This repository has a free License. See `LICENSE.txt` for more information.

To learn about Djura licenses visit our [website](https://www.djura.it/online-platform) or contact us at info@djura.it

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Contact

Using the [Form](https://www.djura.it/get-in-touch) at Djura or info@djura.it

Project Link: [https://github.com/djura-risk-data-engineering/djura-tools](https://github.com/djura-risk-data-engineering/djura-tools)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/djura-risk-data-engineering/djura-tools.svg?style=for-the-badge
[contributors-url]: https://github.com/djura-risk-data-engineering/djura-tools/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/djura-risk-data-engineering/djura-tools.svg?style=for-the-badge
[forks-url]: https://github.com/djura-risk-data-engineering/djura-tools/network/members
[stars-shield]: https://img.shields.io/github/stars/djura-risk-data-engineering/djura-tools.svg?style=for-the-badge
[stars-url]: https://github.com/djura-risk-data-engineering/djura-tools/stargazers
[issues-shield]: https://img.shields.io/github/issues/djura-risk-data-engineering/djura-tools.svg?style=for-the-badge
[issues-url]: https://github.com/djura-risk-data-engineering/djura-tools/issues
[license-shield]: https://img.shields.io/github/license/djura-risk-data-engineering/djura-tools.svg?style=for-the-badge
[license-url]: https://github.com/djura-risk-data-engineering/djura-tools/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/djura

<!-- [product-screenshot]: temp.png -->
[Nuxt.js]: https://img.shields.io/badge/Nuxt-002E3B?style=for-the-badge&logo=nuxtdotjs&logoColor=#00DC82
[Nuxt-url]: https://nuxt.com/
[Vercel]: https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white
[Vercel-url]: https://vercel.com/
[Flask]: https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/en/stable/
[AWS]: https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white
[AWS-url]: https://aws.amazon.com/
[S3]: https://img.shields.io/badge/Amazon%20S3-FF9900?style=for-the-badge&logo=amazons3&logoColor=white
[S3-url]: https://aws.amazon.com/
[Supabase]: https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white
[Supabase-url]: https://supabase.com/
