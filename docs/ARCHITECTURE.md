# Architecture

This document outlines the architecture of the `pdfrebuilder` project.

## Overview

The `pdfrebuilder` is a modular and extensible engine for extracting and rebuilding PDF documents. It is designed to handle various document formats and provide a high-fidelity reconstruction of the original layout.

## Core Components

The architecture is composed of several key components:

- **Engines**: These are responsible for parsing and rendering different document formats. Each format (e.g., PDF, PSD, KRA) has its own engine.
- **Universal Intermediate Data Model (UIDM)**: This is a standardized data structure that represents the content and layout of a document, regardless of its original format. All engines convert their source format to this model.
- **Configuration**: The project uses a flexible configuration system to control the behavior of the engines and other components.
- **CLI**: A command-line interface provides access to the core functionality of the `pdfrebuilder`.

## Data Flow

The typical data flow is as follows:

1.  An input file is passed to the appropriate engine.
2.  The engine parses the file and converts its content into the UIDM.
3.  The UIDM can be manipulated or modified as needed.
4.  A rendering engine takes the UIDM and generates an output file, typically a PDF.
