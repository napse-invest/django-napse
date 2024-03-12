## [1.13.2](https://github.com/napse-invest/django-napse/compare/v1.13.1...v1.13.2) (2024-03-12)


### Bug Fixes

* **api:** exchange_account creation ([45cb17a](https://github.com/napse-invest/django-napse/commit/45cb17af8a34f0e761748eed78cafbdc43dcdfc0))

## [1.13.1](https://github.com/napse-invest/django-napse/compare/v1.13.0...v1.13.1) (2024-03-12)


### Bug Fixes

* **requirements:** pydantic ([08e1256](https://github.com/napse-invest/django-napse/commit/08e1256449e5f449bc97ac4d7b1789e901a0f9a7))

# [1.13.0](https://github.com/napse-invest/django-napse/compare/v1.12.0...v1.13.0) (2024-03-12)


### Bug Fixes

* **naming:** renamed NapseSpace to Space ([9b8a450](https://github.com/napse-invest/django-napse/commit/9b8a450357b6122c2376fd7b946a282bcbef96af))
* **serializer:** fix functionnal issues & add optimizations ([add79fb](https://github.com/napse-invest/django-napse/commit/add79fbf3105065ab8dd316d1993a4d42799f799))
* **serializer:** fix Non subinstances in serializers ([42ec3a4](https://github.com/napse-invest/django-napse/commit/42ec3a41773df49edb321ff77df1d3456827884a))
* **serializer:** replace getter generator by a list ([039809a](https://github.com/napse-invest/django-napse/commit/039809ad5d1c789f26624a2c4cc21dac2fe76cab))


### Features

* **celery:** new history task ([e7f74fa](https://github.com/napse-invest/django-napse/commit/e7f74faf7c9a5dbe3b8a6880e3e002b465af2195))
* **field:** add default ([0704aa1](https://github.com/napse-invest/django-napse/commit/0704aa1f7a144f37ce2aa849f34618962049454e))
* **histories:** added serializers and updated space view ([a267240](https://github.com/napse-invest/django-napse/commit/a267240c3fd50f4b4590fa435edd6586a8c5c999))
* **histories:** added WalletHistories ([a659172](https://github.com/napse-invest/django-napse/commit/a659172fd04815d512282235166ed1aa25b2e240))
* **serializer:** add default to fields & improve drf & django compatibility ([9673316](https://github.com/napse-invest/django-napse/commit/9673316dcac0b694d0bcaf5bae37ceea3a7ddc98))
* **serializer:** add read-only status ([96466eb](https://github.com/napse-invest/django-napse/commit/96466eb315f189eb05514c11a05bad744aebe79f))

# [1.12.0](https://github.com/napse-invest/django-napse/compare/v1.11.0...v1.12.0) (2024-02-27)


### Bug Fixes

* **Fields:** instance_check is now a static method ([6f773db](https://github.com/napse-invest/django-napse/commit/6f773dbdc3a9f0f53236e737e8a0596f3dcc54e2))
* **serializer:** models check works now well with validated data ([dcb249a](https://github.com/napse-invest/django-napse/commit/dcb249a2b8f6912d60fb77e9eeb19948a5382c3c))
* **serializers:** minor fixes for cleaner code ([f92705b](https://github.com/napse-invest/django-napse/commit/f92705b55ce27eca52dbb492ec027fbafdc3eecd))


### Features

* **serializer:** add validations + model manipulation in serializer + UUIDField and DatetimeField ([34317ca](https://github.com/napse-invest/django-napse/commit/34317ca8a5c211d16dde8eddd6befae89049f21b))

# [1.11.0](https://github.com/napse-invest/django-napse/compare/v1.10.4...v1.11.0) (2024-02-21)


### Bug Fixes

* **bot:** add fleet property ([69d2ca4](https://github.com/napse-invest/django-napse/commit/69d2ca431cf2770a1666a68d94248f86a9a80613))
* **bot:** add space containerization ([66bbba6](https://github.com/napse-invest/django-napse/commit/66bbba693fc0b40787ac3f3c343c3c3fe83973f6))
* **bot:** fix bot_in_cluster issues ([386d841](https://github.com/napse-invest/django-napse/commit/386d8414dd7db814cd19373bf0439ef74809ac07))
* **bot:** return only trading bot in endpoints queryset ([b9bc89f](https://github.com/napse-invest/django-napse/commit/b9bc89f6e91359f2740280d6a8b9e5d50d143bf1))
* **cluster:** rework cluster serializer for fleet creation ([3e00688](https://github.com/napse-invest/django-napse/commit/3e00688a5cd66c89eefc8294b2ac387355bad2d5))
* **db_essentials:** now automatically creates the secrets.json file ([0d4c6c6](https://github.com/napse-invest/django-napse/commit/0d4c6c6339ffd1cc191e896815df7f05fe7e6cfb))
* **fleet:** add delta ([0b1fb5c](https://github.com/napse-invest/django-napse/commit/0b1fb5c7d958984af83c87faef2a33b879cb9f74))
* **fleet:** add return to create() & fix auth ([66fcf9c](https://github.com/napse-invest/django-napse/commit/66fcf9c10f24d9f2b5d8c92fce7dafcd241a06b2))
* **fleet:** add space & exchange_account in FleetDetailSerializer ([1d63d9e](https://github.com/napse-invest/django-napse/commit/1d63d9ef8c846cab9f8d6e200db05932871632e4))
* **fleet:** add to_representation method to FleetSerializer ([91fbe69](https://github.com/napse-invest/django-napse/commit/91fbe691eb08e7879509d26020375c40ae6d7c1d))
* **fleet:** export bout_count method to fleet's model ([1d99f34](https://github.com/napse-invest/django-napse/commit/1d99f34310bc4a184dee5385ccbaf5e37eae2d80))
* **fleet:** finished list, retrieve & create fleet endpoints ([aa12309](https://github.com/napse-invest/django-napse/commit/aa123091d4e171479d95fca6127e94cc38af22ba))
* **fleet:** fix create endpoints ([517985f](https://github.com/napse-invest/django-napse/commit/517985f58e4153d1ae5ef2ae968f06e71125aa87))
* **fleet:** fix issue in space's list endpoint behavior ([e7cd0e8](https://github.com/napse-invest/django-napse/commit/e7cd0e89c1dda8746170eebaccdd44fcfdd4ed69))
* **fleet:** fix retrieve endpoint ([ae4c76b](https://github.com/napse-invest/django-napse/commit/ae4c76bfd6596af1d1e6d82c1f746bdc62ff36cc))
* **fleet:** improve fleet serializer ([dd9b5be](https://github.com/napse-invest/django-napse/commit/dd9b5be68127e1989a937dba8e2d1bcf433a89e3))
* **fleet:** rework list and create fleet endpoints ([ae8bfca](https://github.com/napse-invest/django-napse/commit/ae8bfcac5de94ad9e7b14885c06a5cef7a30d0be))
* **fleet:** space_containers=False situation in list endpoint ([b8ca67a](https://github.com/napse-invest/django-napse/commit/b8ca67aa31530ea61c40ce5029f3d2475dfd00d1))
* free bot list are now contained in exchange account ([b90c762](https://github.com/napse-invest/django-napse/commit/b90c762ba11aa677d96ff8d204a66579d84a9774))
* **history:** add bot history to init.py ([4df6892](https://github.com/napse-invest/django-napse/commit/4df6892b836a0cbd63494108d5e362eed81c9812))
* **makefile:** add shell command to makefile ([7cadbbd](https://github.com/napse-invest/django-napse/commit/7cadbbdf762f5ff06e9533c6be5b7461d6c6143e))
* **makefile:** PHONY setup to force it to work ([3142302](https://github.com/napse-invest/django-napse/commit/31423020e1a8b998789b174a297fac8e7127ed09))
* **order:** order serializer ([8ceb1fc](https://github.com/napse-invest/django-napse/commit/8ceb1fc4dda5b3a84a599b0d39b9078c3b7f334a))
* **order:** rename exit amount ([18db2be](https://github.com/napse-invest/django-napse/commit/18db2bebaa9baf103b77d092ad5df759a07b5721))
* **orders:** improve lisiblity of serializer ([f34cfbc](https://github.com/napse-invest/django-napse/commit/f34cfbccf276f381c95311d77faabb8f72445932))
* **setup:** fix pip-tools installation ([8c41f95](https://github.com/napse-invest/django-napse/commit/8c41f95df87547b6c4c02dbd6b3a67610fef56e0))
* **strategy:** add info method ([8d1ac2c](https://github.com/napse-invest/django-napse/commit/8d1ac2c9e7746f9248f22a779fc6a34ca78f693b))
* **wallet:** connect_to() method works even if the connection already exists ([4995227](https://github.com/napse-invest/django-napse/commit/49952276fcdb3e1152b1876da91fd85bab8bec84))
* **workflow:** pyproject.toml can be only modify by owner ([66b8e94](https://github.com/napse-invest/django-napse/commit/66b8e9468cd8ce7818bf482508ace3f66060ffbb))


### Features

* **bot:** add retrieve view ([806bbee](https://github.com/napse-invest/django-napse/commit/806bbee7b6b918a740c52e2cf79ce2aa35fac2d3))
* **order:** create order  serializer ([fb1ca16](https://github.com/napse-invest/django-napse/commit/fb1ca1605bea16decc689e840b28fd1d3c85c544))

## [1.10.4](https://github.com/napse-invest/django-napse/compare/v1.10.3...v1.10.4) (2023-12-21)


### Bug Fixes

* **fleet:** add cluster into serializer ([3f34b00](https://github.com/napse-invest/django-napse/commit/3f34b0066eb4ea018ca9fdc8668f87798ae7811a))

## [1.10.3](https://github.com/napse-invest/django-napse/compare/v1.10.2...v1.10.3) (2023-12-21)


### Bug Fixes

* **docs:** finish mkdocs setup ([a900525](https://github.com/napse-invest/django-napse/commit/a900525b36e19f40cf0019ed35540b673a3727ae))
* **fleet:** improve list endpoint ([039479f](https://github.com/napse-invest/django-napse/commit/039479fb0cd5b1cc15a7ada83cce5b0eb522c73b))
* **space:** remove possible_exchange_account ([2a46272](https://github.com/napse-invest/django-napse/commit/2a4627289b33b537b9c045296cca33090e30d45a))

## [1.10.2](https://github.com/napse-invest/django-napse/compare/v1.10.1...v1.10.2) (2023-11-28)


### Bug Fixes

* **api:** minor fixes ([4a9ff34](https://github.com/napse-invest/django-napse/commit/4a9ff349fe8e9d22e94839e51e10df72aa9298f1))
* **mkdocs & api:** fix currency serializer & mkdocs issues ([ef5a749](https://github.com/napse-invest/django-napse/commit/ef5a7492eb4bab353f259978767742d6a6ce7a4e))
* **mkdocs:** fix mkdocs workflow ([0e9537a](https://github.com/napse-invest/django-napse/commit/0e9537a2241ce2d4483bf5660eca1131e3a321c1))
* **readme:** fix logo ([8aa2d0e](https://github.com/napse-invest/django-napse/commit/8aa2d0eea245bbd1e7373e8f8c487c93ae4647a4))
* **readme:** logo color ([494be3e](https://github.com/napse-invest/django-napse/commit/494be3e65a36f6ae0e369abc05576dfdc0abf8d4))

## [1.10.1](https://github.com/napse-invest/django-napse/compare/v1.10.0...v1.10.1) (2023-11-21)


### Bug Fixes

* **accessibility:** added ease of use tools for the secrets ([5713ca2](https://github.com/napse-invest/django-napse/commit/5713ca2b1464c2dd46e293709dea5c97d550e804))
* **api:** minor changes ([3079288](https://github.com/napse-invest/django-napse/commit/3079288a18c6eacc2496ede51e0c0dcf84629126))
* **history:** remove history serializers ([76c467e](https://github.com/napse-invest/django-napse/commit/76c467e91ab59c024e3b7e38b4e3347fb007e29f))
* **permission:** add relative name between a permission & a NapseSpace ([11ea521](https://github.com/napse-invest/django-napse/commit/11ea52144c89a87e8db750ddd6c94f2d0ca166e5))
* **space & history:** some fixes & space's delta ([c173a3b](https://github.com/napse-invest/django-napse/commit/c173a3bbe25e10a1af6a0afd35af23742d6fe2a4))
* **space:** add get_exchange_account endpoints to spaces and fix circular import on serializers ([64975f2](https://github.com/napse-invest/django-napse/commit/64975f2de85d9ac2229685c299addcf7821d3318))
* **space:** add update endpoints & get_premissions ([7f6d69d](https://github.com/napse-invest/django-napse/commit/7f6d69d1a3b6999fa8e9ddf55ca526e473098772))
* **space:** improvement on views & tests ([3a45999](https://github.com/napse-invest/django-napse/commit/3a45999a2c284a479e3071122fe8694433c10919))
* **wallet serializer:** improve operations ([72a7fa6](https://github.com/napse-invest/django-napse/commit/72a7fa6a870f2ce3aac7f3665fba7630412ec3b3))

# [1.10.0](https://github.com/napse-invest/django-napse/compare/v1.9.0...v1.10.0) (2023-10-20)


### Bug Fixes

* **api-tests:** keys ([b063ad3](https://github.com/napse-invest/django-napse/commit/b063ad3379baaa00603b06b74cd9b12e1d964200))
* **api:** exchangeAccounts endpoints ([62d24d5](https://github.com/napse-invest/django-napse/commit/62d24d54c6cd157ec0fbda60eb634a1e6a46a51e))
* **api:** exchanges api create ([17ea8f1](https://github.com/napse-invest/django-napse/commit/17ea8f1a6effa69e932394500494aaad2c3bfcd2))
* **api:** little changes ([1c99414](https://github.com/napse-invest/django-napse/commit/1c9941493d1720caefb07e50cb3b4d2b0b0dfa44))
* **api:** little improvements ([a1fb18b](https://github.com/napse-invest/django-napse/commit/a1fb18beb20ee47936b3d84e4e0857ccfbb6d750))
* **api:** minor changes to keys ([2eefac3](https://github.com/napse-invest/django-napse/commit/2eefac3e804526a7fbb2d66b1816f39568b9e62a))
* **api:** tests for permission admin ([e68245b](https://github.com/napse-invest/django-napse/commit/e68245b966d936ec6860dfa796d1d66252418518))
* **bot serializers:** add bot serializers ([0be9a58](https://github.com/napse-invest/django-napse/commit/0be9a587e25577ab1263615f0acf6d85c7111c5b))
* **bot:** add view ([92b2184](https://github.com/napse-invest/django-napse/commit/92b2184fdde9f5911c354fe55ca42ff922a4ecb4))
* **cluster:** renaming to template_bot ([bf71708](https://github.com/napse-invest/django-napse/commit/bf71708cfd778f4862be2d9ec68750cc76beea16))
* **error stack:** improve stack error ([e5cfce3](https://github.com/napse-invest/django-napse/commit/e5cfce35c8f1da89062de689b987a79ab9e76402))
* **history:** add history serializer ([11c3270](https://github.com/napse-invest/django-napse/commit/11c327099e93a7ea9fc88ad5d1eadaa4c8a846c1))
* **history:** add history serializers ([d85bdc5](https://github.com/napse-invest/django-napse/commit/d85bdc51ee102951becc417f5dd66d3ccbe584ec))
* **project:** remove useless folder & files in API folder ([2ea8704](https://github.com/napse-invest/django-napse/commit/2ea8704d54f79cf49382b09f95bc56dd2e27f2bb))
* **python-module:** added correct dependencies ([3f388f3](https://github.com/napse-invest/django-napse/commit/3f388f3b22dc59e9281fcf1aac9f33f47b9b3eb3))
* **ruff:** fixed extra iports ([221bbd6](https://github.com/napse-invest/django-napse/commit/221bbd635260da220c8751427884eca396a3d0e2))
* **space:** finish setup of retrieve endpoint ([a763a00](https://github.com/napse-invest/django-napse/commit/a763a00ef6c0c1d63819e51776c02096cc151cb2))
* **workflow:** missing mkdocs-plugin-inline-svg ([271f476](https://github.com/napse-invest/django-napse/commit/271f4762a31521f9a8d4daccd1fd35bc89492d31))
* **workflow:** mkdocs workflow ([cd1d4dd](https://github.com/napse-invest/django-napse/commit/cd1d4ddf5e6588d4bc46395fa2a3ccb720b59911))


### Features

* **api:** keys reworked ([6a35dbd](https://github.com/napse-invest/django-napse/commit/6a35dbdf5ae197f83361075cc3eb3461a0667d6f))

# [1.9.0](https://github.com/napse-invest/django-napse/compare/v1.8.0...v1.9.0) (2023-10-07)


### Bug Fixes

* **tests:** cleaned up prints in tests ([5654ecf](https://github.com/napse-invest/django-napse/commit/5654ecfae85f0530ee393cfb76873863c39ec273))
* **tests:** seperated db tests and api tests ([8a1ab68](https://github.com/napse-invest/django-napse/commit/8a1ab68a3a4def356c5545398ccd78e462f815cd))


### Features

* **api:** integrated restframework_api_keys ([cccd414](https://github.com/napse-invest/django-napse/commit/cccd414ae0bd16bcd8c35ce10554698f983e1214))
* **api:** Tests implemented ([c1d5144](https://github.com/napse-invest/django-napse/commit/c1d5144819e50bfc54e0b3de8cde4a56a98a7707))
* **histories:** Added support for histories. Supported classes are Wallet, NapseSpace, Bot, Fleet, ExchangeAccount ([4cb831b](https://github.com/napse-invest/django-napse/commit/4cb831bc23ad3191cba1ce0046928d94837f7872))

# [1.8.0](https://github.com/napse-invest/django-napse/compare/v1.7.1...v1.8.0) (2023-09-18)


### Features

* **api:** migrated api from dtk to djn ([01a9e1c](https://github.com/napse-invest/django-napse/commit/01a9e1c3731f5a233b79e8a8d4d3ac5a321650aa))

## [1.7.1](https://github.com/napse-invest/django-napse/compare/v1.7.0...v1.7.1) (2023-09-10)


### Bug Fixes

* **fleet:** add values bridges ([28ebc4e](https://github.com/napse-invest/django-napse/commit/28ebc4e27a2cdeb500fcf402b45ba3604a395d30))

# [1.7.0](https://github.com/napse-invest/django-napse/compare/v1.6.6...v1.7.0) (2023-09-09)


### Bug Fixes

* **doublon:** doublon on save ([6e2c7f1](https://github.com/napse-invest/django-napse/commit/6e2c7f1b9b9184667d44216eb6cffbe28ed30d3b))
* makefile ([c150640](https://github.com/napse-invest/django-napse/commit/c15064013ca49ed82fb9c586aef20fdefc25fea7))
* **manage.py:** python path ([ba0ea46](https://github.com/napse-invest/django-napse/commit/ba0ea46c5921e1570b6357186cd11d1295a6b1eb))
* **names:** fix test folder name (tests) and fix space' fleet property ([c599420](https://github.com/napse-invest/django-napse/commit/c599420fa805761ddd80e30641379604109d619f))
* **readme:** update readme with make command ([88edcd6](https://github.com/napse-invest/django-napse/commit/88edcd6012a0536fae606052ad38949b5789aa14))


### Features

* **bridge:** add fleets property ([e72f7e0](https://github.com/napse-invest/django-napse/commit/e72f7e06b42dec4f19926d3ce6ba5284ae122c53))
* **space:** add value property ([89fda45](https://github.com/napse-invest/django-napse/commit/89fda453841cf24bcc73ad72bed9978e34dcf71f))

## [1.6.6](https://github.com/napse-invest/django-napse/compare/v1.6.5...v1.6.6) (2023-09-03)


### Bug Fixes

* celery to 5.3.1 ([7c997da](https://github.com/napse-invest/django-napse/commit/7c997dada6e138134a029057abba2bf572b6d072))
* **celery:** fix task name ([72becf3](https://github.com/napse-invest/django-napse/commit/72becf34b7b5e86d91de22a54bef65c5770a7367))
* **celery:** import tasks ([c80fb7a](https://github.com/napse-invest/django-napse/commit/c80fb7ae6d3ae4dc02e94fa79103446834f33f4e))
* **celery:** reverted imports ([514ef02](https://github.com/napse-invest/django-napse/commit/514ef027d33ea985eee4c0d1f22f6346ed54cd2b))
* **celery:** version bumped down to 5.3.1 ([1c7b66d](https://github.com/napse-invest/django-napse/commit/1c7b66d39d4697649b309b9d178a9a9daa1b87cb))

## [1.6.5](https://github.com/napse-invest/django-napse/compare/v1.6.4...v1.6.5) (2023-08-20)


### Bug Fixes

* **pypi:** added utils ([161c5ed](https://github.com/napse-invest/django-napse/commit/161c5edfb4e827eafba3ba3ca6da12af3aafef9e))

## [1.6.4](https://github.com/napse-invest/django-napse/compare/v1.6.3...v1.6.4) (2023-08-20)


### Bug Fixes

* **pypi:** requirements ([580a918](https://github.com/napse-invest/django-napse/commit/580a918f32a092c1c7847c144fa1e47dab95afae))

## [1.6.3](https://github.com/napse-invest/django-napse/compare/v1.6.2...v1.6.3) (2023-08-20)


### Bug Fixes

* **pypi:** adding modules ([91d36e6](https://github.com/napse-invest/django-napse/commit/91d36e69ff23eba7525fc0d49ac9574e24b749a6))

## [1.6.2](https://github.com/napse-invest/django-napse/compare/v1.6.1...v1.6.2) (2023-08-20)


### Bug Fixes

* **ci:** added space ([ca3cb5d](https://github.com/napse-invest/django-napse/commit/ca3cb5d901cc15395e341059caa9f7372a6466be))

## [1.6.1](https://github.com/napse-invest/django-napse/compare/v1.6.0...v1.6.1) (2023-08-20)


### Bug Fixes

* **ci:** pypi ([4ccc241](https://github.com/napse-invest/django-napse/commit/4ccc2410457e5337fb15517b3d824f4a031146cd))
* **ci:** tables missing ([aa98201](https://github.com/napse-invest/django-napse/commit/aa9820111dc8062a573beefe032f5e452d953753))
* **ruff:** unused import ([759d5a9](https://github.com/napse-invest/django-napse/commit/759d5a9e1223ca21f6a87b74ecf228e435811b41))
* **test:** failing test ([c30f705](https://github.com/napse-invest/django-napse/commit/c30f705683d5caee8157d6902b586c5ce88aec65))

# [1.6.0](https://github.com/napse-invest/django-napse/compare/v1.5.2...v1.6.0) (2023-08-20)


### Bug Fixes

* **mbp-and-ruff:** fixed to remove eval ([341c5cc](https://github.com/napse-invest/django-napse/commit/341c5ccb32f8524da17febf78d59813d96134663))
* **mbp:** duplicate line because of isort ([6348c4b](https://github.com/napse-invest/django-napse/commit/6348c4b2e8983a593738826d0bd542ba2c7b64ff))
* **mbp:** removed eval ([7b4aa76](https://github.com/napse-invest/django-napse/commit/7b4aa765e038a93c66c3d46e648d0f5a9593680f))
* **ruff:** added RUF012 back ([b3ea928](https://github.com/napse-invest/django-napse/commit/b3ea928514f5dc4a602b38f892a534f1cd8a343c))
* **ruff:** isort ([fbac244](https://github.com/napse-invest/django-napse/commit/fbac244f30cd75fdfd5d32778020e6a81e6a3d94))


### Features

* **fleet:** implemented and tested ([7f8873e](https://github.com/napse-invest/django-napse/commit/7f8873ece6be015094b47771ed7ed06a06f47960))

## [1.5.2](https://github.com/napse-invest/django-napse/compare/v1.5.1...v1.5.2) (2023-08-16)


### Bug Fixes

* **workflow:** trigger new release ([25a74ad](https://github.com/napse-invest/django-napse/commit/25a74adf19c109e941fb31d6486d9a87df9bb36c))

## [1.5.1](https://github.com/napse-invest/django-napse/compare/v1.5.0...v1.5.1) (2023-08-16)


### Bug Fixes

* **workflow:** tag version in setup.py for pypi ([ee4e74e](https://github.com/napse-invest/django-napse/commit/ee4e74e894a2fbf7c347e60e302e50db3e0c70fa))

# [1.5.0](https://github.com/napse-invest/django-napse/compare/v1.4.0...v1.5.0) (2023-08-16)


### Features

* **workflow:** pypi workflow ([340dbbe](https://github.com/napse-invest/django-napse/commit/340dbbe64ab35901c5b5800f2331850b5b7289e5))

# [1.4.0](https://github.com/napse-invest/django-napse/compare/v1.3.0...v1.4.0) (2023-08-14)


### Bug Fixes

* **ci:** added timeout ([8ed9571](https://github.com/napse-invest/django-napse/commit/8ed95712ce0b7eaec600ed472e240f3f572f4a9b))
* **plugins:** minor adjustments ([cc130a3](https://github.com/napse-invest/django-napse/commit/cc130a3aa4f74d5cf321182386e0eeefb51ae26c))
* **test:** tests too long because of sims ([a7ce1b7](https://github.com/napse-invest/django-napse/commit/a7ce1b782ce275a6e46c9eb255a9e0dab7ec89ae))


### Features

* **dca-bot:** implemented model and tests ([78b67f0](https://github.com/napse-invest/django-napse/commit/78b67f0c0f6465af636018570a60facedbb71bd2))
* **plugins:** implemented mbp plugin ([0bf8431](https://github.com/napse-invest/django-napse/commit/0bf8431ab455a6eaca0b5f3455c94a0030c623a8))
* **plugins:** mbp, sbv, lbo itegrated and tested. ([51a7e8c](https://github.com/napse-invest/django-napse/commit/51a7e8c77f26d3111eeaa1908c74a9fc9a439b85))
* **turbo-dca:** enhanced version of the dca bot ([801d1e0](https://github.com/napse-invest/django-napse/commit/801d1e05b28ac84412628a4643903b8ac9c5627c))

# [1.3.0](https://github.com/napse-invest/django-napse/compare/v1.2.0...v1.3.0) (2023-08-13)


### Bug Fixes

* **tests:** fixed simulation test breaking because of lacking keys "amounts" & "tickers" ([1b45b02](https://github.com/napse-invest/django-napse/commit/1b45b0229955360ef7280158892dcdba5e271563))


### Features

* **modifications:** first modification implemented and tested in quicksim ([bd0b157](https://github.com/napse-invest/django-napse/commit/bd0b1577cc229e4778ba57a1364fb411e4a7f21d))
* **simulations:** First implementation of simutions and tests ([e0622eb](https://github.com/napse-invest/django-napse/commit/e0622eb9e12416dafa7be0fb37a76292f6bd2df4))
* **simulations:** polished the feature, just lacks plugins ([6a052c3](https://github.com/napse-invest/django-napse/commit/6a052c3c8d93a19b603aee5d351a0f2d396e9c3d))

# [1.2.0](https://github.com/napse-invest/django-napse/compare/v1.1.0...v1.2.0) (2023-08-10)


### Bug Fixes

* **ci:** removed BINANCE keys from pipelines ([aeeacc3](https://github.com/napse-invest/django-napse/commit/aeeacc3e184bb2747be53b3c5a09974eb5ecb7c7))
* **ci:** test if changes to secrets worked ([b91d1c4](https://github.com/napse-invest/django-napse/commit/b91d1c4a39c6623351c989d3fa475e1182fd7fde))
* **controller:** moved to exchange_account level ([ebff8f7](https://github.com/napse-invest/django-napse/commit/ebff8f7d4ed03ac6dd05369870717dfb6c7076e1))


### Features

* **simulations:** models added and tested ([d75da60](https://github.com/napse-invest/django-napse/commit/d75da60624a8bb09cf44c84e2220e4fe666fce12))
* **tests:** Dataset ([89f83e7](https://github.com/napse-invest/django-napse/commit/89f83e777d94880dc906c0da734e67e0725686ed))

# [1.1.0](https://github.com/napse-invest/django-napse/compare/v1.0.0...v1.1.0) (2023-08-08)


### Bug Fixes

* **ci:** branch workflow ([29e562d](https://github.com/napse-invest/django-napse/commit/29e562de813f6e1d6f557e9878c71b3bfa57d1da))
* **ci:** checks ([7a8d078](https://github.com/napse-invest/django-napse/commit/7a8d078329c9d59f2fc0698b88fddeb43fdff1c5))
* **ci:** concluding t3.micro is the smallest we can go ([b4382e0](https://github.com/napse-invest/django-napse/commit/b4382e0761676a0761896b87df3c6a262f0022b3))
* **ci:** fixed django.yml ([1e84881](https://github.com/napse-invest/django-napse/commit/1e84881aebba0a168715ca8c3375200819c84d55))
* **ci:** gh actions ([1dfcb12](https://github.com/napse-invest/django-napse/commit/1dfcb12e1270ba8ac481f913e5da02c5ad3adf4d))
* **ci:** secrets in pipelines ([706c1f6](https://github.com/napse-invest/django-napse/commit/706c1f6226debd04468005e371add80c6ac45e98))
* **ci:** secrets not found ([0af933a](https://github.com/napse-invest/django-napse/commit/0af933af8b8b7f3928d565ce8f076b3a2516d488))
* **ci:** secrets.json ([77b463a](https://github.com/napse-invest/django-napse/commit/77b463af19c3791a2c4143196d519014560d8ad4))
* **ci:** secrets.json ([b6d5930](https://github.com/napse-invest/django-napse/commit/b6d5930828bc1918f287540abf8bb488e707e15e))
* **ci:** self hosted runners ([2409a67](https://github.com/napse-invest/django-napse/commit/2409a678e4a73e8e3853c3d71e2d47da6c90434a))
* **ci:** t3.small -> t3.micro ([313f27d](https://github.com/napse-invest/django-napse/commit/313f27d9d434838e9c04fe2ababd5a1206bbe991))
* **ci:** testing t3.nano ([f66c5ca](https://github.com/napse-invest/django-napse/commit/f66c5cac05f1b22230f877475802c81080daf4b7))
* **merge:** resolved conflicts ([fb8b499](https://github.com/napse-invest/django-napse/commit/fb8b499f7364d6545bf3de593f6e13b84e8a299c))
* **node:** max old space 1400 ([db40cfe](https://github.com/napse-invest/django-napse/commit/db40cfedcea9130253bd6a585d2e4471f44b5134))
* **tests:** wallet tests refactored ([800d6a1](https://github.com/napse-invest/django-napse/commit/800d6a15a630bf95f9193e0479b95a31ecd5a8fd))


### Features

* **bot-config:** reworked into individual classes for each config type ([2a0bd32](https://github.com/napse-invest/django-napse/commit/2a0bd323c170ae8d340dad50cb44844f73760067))
* **bots-and-tests:** New bot architecture works and clean tests are setup ([54fdfca](https://github.com/napse-invest/django-napse/commit/54fdfca5ac31c06ffdb02be636b4b48170a4ab53))
* **bots:** rework partially implemented ([34d0c6d](https://github.com/napse-invest/django-napse/commit/34d0c6de61df60ae1448f67a45ddc3a9277434e1))
* **ci:** self hosted runners ([fe1a456](https://github.com/napse-invest/django-napse/commit/fe1a4567844b29dedad8b50082187812336c7fb8))
* **DataSet:** Initial functionality and tests ([7e074f0](https://github.com/napse-invest/django-napse/commit/7e074f07cdbe0d5f378f9d1f3bf96715d71c37cd))
* **tests:** refactoring tests and added the exchange variation ([78dcbfb](https://github.com/napse-invest/django-napse/commit/78dcbfbca3d87dbae698db4b0b7b6548dd5d817d))

# 1.0.0 (2023-08-06)


### Bug Fixes

* **ci:** 'on' in django.yml ([340a708](https://github.com/napse-invest/django-napse/commit/340a7083b5684ba6f6527e5c2ad9e17a8513e64f))
* **ci:** add test step ([dda5ef6](https://github.com/napse-invest/django-napse/commit/dda5ef67b711b8be6e14bf1469761d75585acb8a))
* **ci:** development requirements & pip tools ([0723bba](https://github.com/napse-invest/django-napse/commit/0723bba1c4fc90a66a7df23241dfff54581fa024))
* **ci:** export pythonpath ([9333cdc](https://github.com/napse-invest/django-napse/commit/9333cdccd4be8ce34b50e98787a36cb3c20533aa))
* **ci:** manage.py path ([2c4e27f](https://github.com/napse-invest/django-napse/commit/2c4e27f7eb5f045950420ebd62d5614caf972689))
* **ci:** remove python architecture ([01c975d](https://github.com/napse-invest/django-napse/commit/01c975d3d242d2f5222e04cb19a00cbe594406bc))
* **ci:** remove strategy ([bd517d8](https://github.com/napse-invest/django-napse/commit/bd517d8e33585d585d9db3faa656b79af582179b))
* **ci:** requirements ([ddd64fb](https://github.com/napse-invest/django-napse/commit/ddd64fbd5804482ab7059eab70576ac838bdab6d))
* **ci:** requirements ([1574e5e](https://github.com/napse-invest/django-napse/commit/1574e5e563583b0f876f40ceb5e4aa685b3f5622))
* **ci:** requirements ([6b724af](https://github.com/napse-invest/django-napse/commit/6b724af2a33b69958525d5d4c60a458c73b5cbd5))
* **ci:** requirements ([d1ea728](https://github.com/napse-invest/django-napse/commit/d1ea728e9e73ee058f8031eaa49032f31024fc4d))
* **coverage:** add label ([6600fd6](https://github.com/napse-invest/django-napse/commit/6600fd6240d3864490a2944e758cb78c30e74a97))
* **coverage:** auto build ./badges folder ([465b80c](https://github.com/napse-invest/django-napse/commit/465b80c8149c515501e281f44e7cd6aa2be3a8ba))
* **coverage:** cvg_result ([80aaffd](https://github.com/napse-invest/django-napse/commit/80aaffd01bbce874fe905680d233d7de522ec8f7))
* **coverage:** tmp ([485def1](https://github.com/napse-invest/django-napse/commit/485def139a664c7aa9acf2fe437653cd0c232615))
* **django-apps:** added labels to make clearer and less error prone ([268f7fe](https://github.com/napse-invest/django-napse/commit/268f7fe00d8144dad6482a511763c90a7308f7f7))
* **readme:** update title ([a14a615](https://github.com/napse-invest/django-napse/commit/a14a615adaf969981234069138693e3434cd7504))
* **release:** workflow optimization ([f131c6e](https://github.com/napse-invest/django-napse/commit/f131c6e534c87eb251d35119a23cbeb8c1f8b266))
* **setup:** fixed pip ([ff961d2](https://github.com/napse-invest/django-napse/commit/ff961d2261ebb2beed1d30e93ab4a0517f57513e))
* **setup:** reworked slightly ([517c044](https://github.com/napse-invest/django-napse/commit/517c04494dde31f8f371571a5349c7ca3bf37935))
* **test:** ... ([4676c9f](https://github.com/napse-invest/django-napse/commit/4676c9f4b8a49d885fb522436080319c496ee5ae))
* **workflow:** fix indend issue ([6710f3a](https://github.com/napse-invest/django-napse/commit/6710f3ae30ce4ad35ddd3419920c4e23eaf80234))
* **workflow:** github token ([a59ae33](https://github.com/napse-invest/django-napse/commit/a59ae330990122d14682dfed9ab5b2aafae27332))
* **workflow:** optimization of release.yml ([af45125](https://github.com/napse-invest/django-napse/commit/af45125c74b8d9ed58874eeb3d666841e27cb035))
* **workflow:** release ([140ff74](https://github.com/napse-invest/django-napse/commit/140ff747fd9dfc648cf4c5caaafff7dc51d9d817))
* **workflow:** release.yml ([7063c8c](https://github.com/napse-invest/django-napse/commit/7063c8c3bfb70ffce841bf3dcf53d555a707640d))
* **workflow:** remove --ci params in release workflow ([7a11d54](https://github.com/napse-invest/django-napse/commit/7a11d54f97b5c512194e5832fa9fdf52d7486154))
* **workflow:** remove test badge ([6a03ce4](https://github.com/napse-invest/django-napse/commit/6a03ce425e295a4cf357b639b2bcac64506c2d3e))
* **workflow:** update release.yml ([28bab08](https://github.com/napse-invest/django-napse/commit/28bab08cdf4df3843f191505908bb87805be7f06))


### Features

* **celery:** initial setup ([7d7fb19](https://github.com/napse-invest/django-napse/commit/7d7fb19cddb585b740c5f4720235deaa9d8c5e03))
* **ci:** --parallel on django test ([b259ef0](https://github.com/napse-invest/django-napse/commit/b259ef0cef798136507e07bf306ef460b55bec6e))
* **ci:** add ruff and remove python version matric ([f2fbb74](https://github.com/napse-invest/django-napse/commit/f2fbb74be9339a5fc885bc1d566a310bc2f98534))
* **ci:** django workflow ([c1072db](https://github.com/napse-invest/django-napse/commit/c1072db0fca2a7add5d99f48663c8e0625a43d25))
* **ci:** remove test file ([a4369c4](https://github.com/napse-invest/django-napse/commit/a4369c4f6703352c89d57b9f6be6468cfc9a4ff9))
* **ci:** setup workflow ([85c7494](https://github.com/napse-invest/django-napse/commit/85c74948fb817f59953df9585eeb0843f1ab5e3a))
* **coverage:** add action for anybadge ([4d572cb](https://github.com/napse-invest/django-napse/commit/4d572cb593de97a95bca6ea575154bee8389e237))
* **coverage:** add coverage badge to workflow ([1f1e81e](https://github.com/napse-invest/django-napse/commit/1f1e81e63ce64859beec3a786d92052df77f3388))
* **coverage:** does readme works ? ([f7545ba](https://github.com/napse-invest/django-napse/commit/f7545ba669974a781025a683cd82b0f4352de7a8))
* **db:** First go at setting up accounts and exchanges ([ead1e8e](https://github.com/napse-invest/django-napse/commit/ead1e8e7004206fd0294327623987ccf634bb39f))
* **readme:** add tag badge ([c66830b](https://github.com/napse-invest/django-napse/commit/c66830b1710aa89294c11282dce31c9c536ada22))
* **readme:** update readme ([a877c0b](https://github.com/napse-invest/django-napse/commit/a877c0bac27b82d4ca4e953cd803a60325fe478e))
* **setup:** add windows setup ([65c12e4](https://github.com/napse-invest/django-napse/commit/65c12e46afe6589099af091df179db50e986a328))
* **svg:** new svg ([482acf7](https://github.com/napse-invest/django-napse/commit/482acf701eb3b31764d7825bc5c60a3e5f782292))
* **transactions:** all tests ([ad3d19f](https://github.com/napse-invest/django-napse/commit/ad3d19f81b96116b8e0a58534a3e47bb6f5a03d1))
* **workflow:** add check source branch ([edadfa1](https://github.com/napse-invest/django-napse/commit/edadfa12a534086fe74fb9af239db47240f216a1))
* **workflow:** setup versionning workflow ([2ee2440](https://github.com/napse-invest/django-napse/commit/2ee2440018b9cadcf6f5b8bb423cbee2b561f2c2))

## [1.1.2](https://github.com/napse-invest/django-napse/compare/v1.1.1...v1.1.2) (2023-08-05)


### Bug Fixes

* **workflow:** optimization of release.yml ([af45125](https://github.com/napse-invest/django-napse/commit/af45125c74b8d9ed58874eeb3d666841e27cb035))

## [1.1.1](https://github.com/napse-invest/django-napse/compare/v1.1.0...v1.1.1) (2023-08-05)


### Bug Fixes

* **workflow:** release ([140ff74](https://github.com/napse-invest/django-napse/commit/140ff747fd9dfc648cf4c5caaafff7dc51d9d817))
* **workflow:** release.yml ([7063c8c](https://github.com/napse-invest/django-napse/commit/7063c8c3bfb70ffce841bf3dcf53d555a707640d))
* **workflow:** remove --ci params in release workflow ([7a11d54](https://github.com/napse-invest/django-napse/commit/7a11d54f97b5c512194e5832fa9fdf52d7486154))
* **workflow:** remove test badge ([6a03ce4](https://github.com/napse-invest/django-napse/commit/6a03ce425e295a4cf357b639b2bcac64506c2d3e))

# [1.1.0](https://github.com/napse-invest/django-napse/compare/v1.0.1...v1.1.0) (2023-08-05)


### Bug Fixes

* **test:** ... ([4676c9f](https://github.com/napse-invest/django-napse/commit/4676c9f4b8a49d885fb522436080319c496ee5ae))


### Features

* **readme:** update readme ([a877c0b](https://github.com/napse-invest/django-napse/commit/a877c0bac27b82d4ca4e953cd803a60325fe478e))

## [1.0.1](https://github.com/napse-invest/django-napse/compare/v1.0.0...v1.0.1) (2023-08-05)


### Bug Fixes

* **release:** workflow optimization ([f131c6e](https://github.com/napse-invest/django-napse/commit/f131c6e534c87eb251d35119a23cbeb8c1f8b266))

# 1.0.0 (2023-08-05)


### Bug Fixes

* **ci:** 'on' in django.yml ([340a708](https://github.com/napse-invest/django-napse/commit/340a7083b5684ba6f6527e5c2ad9e17a8513e64f))
* **ci:** add test step ([dda5ef6](https://github.com/napse-invest/django-napse/commit/dda5ef67b711b8be6e14bf1469761d75585acb8a))
* **ci:** development requirements & pip tools ([0723bba](https://github.com/napse-invest/django-napse/commit/0723bba1c4fc90a66a7df23241dfff54581fa024))
* **ci:** export pythonpath ([9333cdc](https://github.com/napse-invest/django-napse/commit/9333cdccd4be8ce34b50e98787a36cb3c20533aa))
* **ci:** manage.py path ([2c4e27f](https://github.com/napse-invest/django-napse/commit/2c4e27f7eb5f045950420ebd62d5614caf972689))
* **ci:** remove python architecture ([01c975d](https://github.com/napse-invest/django-napse/commit/01c975d3d242d2f5222e04cb19a00cbe594406bc))
* **ci:** remove strategy ([bd517d8](https://github.com/napse-invest/django-napse/commit/bd517d8e33585d585d9db3faa656b79af582179b))
* **ci:** requirements ([ddd64fb](https://github.com/napse-invest/django-napse/commit/ddd64fbd5804482ab7059eab70576ac838bdab6d))
* **ci:** requirements ([1574e5e](https://github.com/napse-invest/django-napse/commit/1574e5e563583b0f876f40ceb5e4aa685b3f5622))
* **ci:** requirements ([6b724af](https://github.com/napse-invest/django-napse/commit/6b724af2a33b69958525d5d4c60a458c73b5cbd5))
* **ci:** requirements ([d1ea728](https://github.com/napse-invest/django-napse/commit/d1ea728e9e73ee058f8031eaa49032f31024fc4d))
* **coverage:** add label ([6600fd6](https://github.com/napse-invest/django-napse/commit/6600fd6240d3864490a2944e758cb78c30e74a97))
* **coverage:** auto build ./badges folder ([465b80c](https://github.com/napse-invest/django-napse/commit/465b80c8149c515501e281f44e7cd6aa2be3a8ba))
* **coverage:** cvg_result ([80aaffd](https://github.com/napse-invest/django-napse/commit/80aaffd01bbce874fe905680d233d7de522ec8f7))
* **coverage:** tmp ([485def1](https://github.com/napse-invest/django-napse/commit/485def139a664c7aa9acf2fe437653cd0c232615))
* **django-apps:** added labels to make clearer and less error prone ([268f7fe](https://github.com/napse-invest/django-napse/commit/268f7fe00d8144dad6482a511763c90a7308f7f7))
* **readme:** update title ([a14a615](https://github.com/napse-invest/django-napse/commit/a14a615adaf969981234069138693e3434cd7504))
* **setup:** fixed pip ([ff961d2](https://github.com/napse-invest/django-napse/commit/ff961d2261ebb2beed1d30e93ab4a0517f57513e))
* **setup:** reworked slightly ([517c044](https://github.com/napse-invest/django-napse/commit/517c04494dde31f8f371571a5349c7ca3bf37935))
* **workflow:** fix indend issue ([6710f3a](https://github.com/napse-invest/django-napse/commit/6710f3ae30ce4ad35ddd3419920c4e23eaf80234))
* **workflow:** github token ([a59ae33](https://github.com/napse-invest/django-napse/commit/a59ae330990122d14682dfed9ab5b2aafae27332))
* **workflow:** update release.yml ([28bab08](https://github.com/napse-invest/django-napse/commit/28bab08cdf4df3843f191505908bb87805be7f06))


### Features

* **celery:** initial setup ([7d7fb19](https://github.com/napse-invest/django-napse/commit/7d7fb19cddb585b740c5f4720235deaa9d8c5e03))
* **ci:** --parallel on django test ([b259ef0](https://github.com/napse-invest/django-napse/commit/b259ef0cef798136507e07bf306ef460b55bec6e))
* **ci:** add ruff and remove python version matric ([f2fbb74](https://github.com/napse-invest/django-napse/commit/f2fbb74be9339a5fc885bc1d566a310bc2f98534))
* **ci:** django workflow ([c1072db](https://github.com/napse-invest/django-napse/commit/c1072db0fca2a7add5d99f48663c8e0625a43d25))
* **ci:** remove test file ([a4369c4](https://github.com/napse-invest/django-napse/commit/a4369c4f6703352c89d57b9f6be6468cfc9a4ff9))
* **ci:** setup workflow ([85c7494](https://github.com/napse-invest/django-napse/commit/85c74948fb817f59953df9585eeb0843f1ab5e3a))
* **coverage:** add action for anybadge ([4d572cb](https://github.com/napse-invest/django-napse/commit/4d572cb593de97a95bca6ea575154bee8389e237))
* **coverage:** add coverage badge to workflow ([1f1e81e](https://github.com/napse-invest/django-napse/commit/1f1e81e63ce64859beec3a786d92052df77f3388))
* **coverage:** does readme works ? ([f7545ba](https://github.com/napse-invest/django-napse/commit/f7545ba669974a781025a683cd82b0f4352de7a8))
* **db:** First go at setting up accounts and exchanges ([ead1e8e](https://github.com/napse-invest/django-napse/commit/ead1e8e7004206fd0294327623987ccf634bb39f))
* **setup:** add windows setup ([65c12e4](https://github.com/napse-invest/django-napse/commit/65c12e46afe6589099af091df179db50e986a328))
* **svg:** new svg ([482acf7](https://github.com/napse-invest/django-napse/commit/482acf701eb3b31764d7825bc5c60a3e5f782292))
* **transactions:** all tests ([ad3d19f](https://github.com/napse-invest/django-napse/commit/ad3d19f81b96116b8e0a58534a3e47bb6f5a03d1))
* **workflow:** setup versionning workflow ([2ee2440](https://github.com/napse-invest/django-napse/commit/2ee2440018b9cadcf6f5b8bb423cbee2b561f2c2))

# 1.0.0 (2023-08-05)


### Bug Fixes

* **ci:** 'on' in django.yml ([340a708](https://github.com/napse-invest/django-napse/commit/340a7083b5684ba6f6527e5c2ad9e17a8513e64f))
* **ci:** add test step ([dda5ef6](https://github.com/napse-invest/django-napse/commit/dda5ef67b711b8be6e14bf1469761d75585acb8a))
* **ci:** development requirements & pip tools ([0723bba](https://github.com/napse-invest/django-napse/commit/0723bba1c4fc90a66a7df23241dfff54581fa024))
* **ci:** export pythonpath ([9333cdc](https://github.com/napse-invest/django-napse/commit/9333cdccd4be8ce34b50e98787a36cb3c20533aa))
* **ci:** manage.py path ([2c4e27f](https://github.com/napse-invest/django-napse/commit/2c4e27f7eb5f045950420ebd62d5614caf972689))
* **ci:** remove python architecture ([01c975d](https://github.com/napse-invest/django-napse/commit/01c975d3d242d2f5222e04cb19a00cbe594406bc))
* **ci:** remove strategy ([bd517d8](https://github.com/napse-invest/django-napse/commit/bd517d8e33585d585d9db3faa656b79af582179b))
* **ci:** requirements ([ddd64fb](https://github.com/napse-invest/django-napse/commit/ddd64fbd5804482ab7059eab70576ac838bdab6d))
* **ci:** requirements ([1574e5e](https://github.com/napse-invest/django-napse/commit/1574e5e563583b0f876f40ceb5e4aa685b3f5622))
* **ci:** requirements ([6b724af](https://github.com/napse-invest/django-napse/commit/6b724af2a33b69958525d5d4c60a458c73b5cbd5))
* **ci:** requirements ([d1ea728](https://github.com/napse-invest/django-napse/commit/d1ea728e9e73ee058f8031eaa49032f31024fc4d))
* **coverage:** add label ([6600fd6](https://github.com/napse-invest/django-napse/commit/6600fd6240d3864490a2944e758cb78c30e74a97))
* **coverage:** auto build ./badges folder ([465b80c](https://github.com/napse-invest/django-napse/commit/465b80c8149c515501e281f44e7cd6aa2be3a8ba))
* **coverage:** cvg_result ([80aaffd](https://github.com/napse-invest/django-napse/commit/80aaffd01bbce874fe905680d233d7de522ec8f7))
* **coverage:** tmp ([485def1](https://github.com/napse-invest/django-napse/commit/485def139a664c7aa9acf2fe437653cd0c232615))
* **django-apps:** added labels to make clearer and less error prone ([268f7fe](https://github.com/napse-invest/django-napse/commit/268f7fe00d8144dad6482a511763c90a7308f7f7))
* **readme:** update title ([a14a615](https://github.com/napse-invest/django-napse/commit/a14a615adaf969981234069138693e3434cd7504))
* **setup:** fixed pip ([ff961d2](https://github.com/napse-invest/django-napse/commit/ff961d2261ebb2beed1d30e93ab4a0517f57513e))
* **setup:** reworked slightly ([517c044](https://github.com/napse-invest/django-napse/commit/517c04494dde31f8f371571a5349c7ca3bf37935))
* **workflow:** fix indend issue ([6710f3a](https://github.com/napse-invest/django-napse/commit/6710f3ae30ce4ad35ddd3419920c4e23eaf80234))
* **workflow:** github token ([a59ae33](https://github.com/napse-invest/django-napse/commit/a59ae330990122d14682dfed9ab5b2aafae27332))
* **workflow:** update release.yml ([28bab08](https://github.com/napse-invest/django-napse/commit/28bab08cdf4df3843f191505908bb87805be7f06))


### Features

* **celery:** initial setup ([7d7fb19](https://github.com/napse-invest/django-napse/commit/7d7fb19cddb585b740c5f4720235deaa9d8c5e03))
* **ci:** --parallel on django test ([b259ef0](https://github.com/napse-invest/django-napse/commit/b259ef0cef798136507e07bf306ef460b55bec6e))
* **ci:** add ruff and remove python version matric ([f2fbb74](https://github.com/napse-invest/django-napse/commit/f2fbb74be9339a5fc885bc1d566a310bc2f98534))
* **ci:** django workflow ([c1072db](https://github.com/napse-invest/django-napse/commit/c1072db0fca2a7add5d99f48663c8e0625a43d25))
* **ci:** remove test file ([a4369c4](https://github.com/napse-invest/django-napse/commit/a4369c4f6703352c89d57b9f6be6468cfc9a4ff9))
* **ci:** setup workflow ([85c7494](https://github.com/napse-invest/django-napse/commit/85c74948fb817f59953df9585eeb0843f1ab5e3a))
* **coverage:** add action for anybadge ([4d572cb](https://github.com/napse-invest/django-napse/commit/4d572cb593de97a95bca6ea575154bee8389e237))
* **coverage:** add coverage badge to workflow ([1f1e81e](https://github.com/napse-invest/django-napse/commit/1f1e81e63ce64859beec3a786d92052df77f3388))
* **coverage:** does readme works ? ([f7545ba](https://github.com/napse-invest/django-napse/commit/f7545ba669974a781025a683cd82b0f4352de7a8))
* **db:** First go at setting up accounts and exchanges ([ead1e8e](https://github.com/napse-invest/django-napse/commit/ead1e8e7004206fd0294327623987ccf634bb39f))
* **setup:** add windows setup ([65c12e4](https://github.com/napse-invest/django-napse/commit/65c12e46afe6589099af091df179db50e986a328))
* **svg:** new svg ([482acf7](https://github.com/napse-invest/django-napse/commit/482acf701eb3b31764d7825bc5c60a3e5f782292))
* **transactions:** all tests ([ad3d19f](https://github.com/napse-invest/django-napse/commit/ad3d19f81b96116b8e0a58534a3e47bb6f5a03d1))
* **workflow:** setup versionning workflow ([2ee2440](https://github.com/napse-invest/django-napse/commit/2ee2440018b9cadcf6f5b8bb423cbee2b561f2c2))
