# Forms and Validation in Symfony

Use this reference when you build form types, transformers, events, collections or multi-step flows, map request data onto DTOs, or write Validator constraints, custom constraints, groups and sequences in a Symfony 5.4..8.x project.

## Table of Contents

- [Form Types](#form-types)
- [Data Transformers](#data-transformers)
- [Form Events](#form-events)
- [Collections](#collections)
- [Multi-Step Form Flows](#multi-step-form-flows)
- [Request Payload Mapping](#request-payload-mapping)
- [Validator Constraints](#validator-constraints)
- [Custom Constraints](#custom-constraints)
- [Groups and Sequences](#groups-and-sequences)
- [Sources](#sources)

## Form Types

**What it is.** A form type is a single input (`TextType`), a group of fields (`PostalAddressType`) or a whole `<form>` (`UserProfileType`). `FormType` is the root parent of all types; custom types inherit through `getParent()`. Form classes implement `FormTypeInterface`, but extending `AbstractType` is the better choice.

**When to use.** Server-rendered forms: `handleRequest()` writes submitted data into the object, the object is validated, and an invalid form is rendered again with errors.

**How it binds data.**
- Set `data_class` explicitly in the form type; it is not required but recommended so embedded forms work later. Without an object or `data_class` the form returns an array.
- A field reads and writes the matching property through PropertyAccess. A non-public property must have a getter and a setter. `property_path` maps to another property, including nested ones (`category.name`).
- `mapped => false` is for fields not stored in the object; read them with `$form->get('agreeTerms')->getData()`.
- Constraints live on the data class (attributes) or in the field's `constraints` option. Form validation needs `symfony/validator`.

**Pitfalls.**
- Call `createView()` after `handleRequest()`. Otherwise changes made in `*_SUBMIT` events, such as validation errors, do not reach the view.
- If a transformer fails, the form or the affected field may be marked as not synchronized (`isSynchronized()`).
- `submit()` expects the same fields the form class defines; nested forms expect an array.
- For PATCH, pass `false` as the second argument of `submit()`. Missing fields are then removed from the form object instead of being set to `null`, and validation applies only to the submitted fields.
- CSRF protection is built into the Form component but must be explicitly enabled or replaced with a custom solution. Disable it per form with `['csrf_protection' => false]`.
- `validation_groups => false` disables validation, but the form still runs basic integrity checks.

```php
final class TaskType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('task', TextType::class)
            ->add('dueDate', DateType::class)
            ->add('save', SubmitType::class);
    }
}

public function new(Request $request): Response
{
    $task = new Task();
    $form = $this->createForm(TaskType::class, $task);
    $form->handleRequest($request);

    if ($form->isSubmitted() && $form->isValid()) {
        return $this->redirectToRoute('task_success');
    }

    return $this->render('task/new.html.twig', ['form' => $form]);
}
```

**Versions.**

| Version | Change |
| --- | --- |
| 5.2 | `legacy_error_messages` option; set it to `false` for the newer messages |
| 5.3 | `renderForm()` renders the template and sets HTTP 422 when the submitted form is invalid. Before 5.3 controllers passed `$form->createView()` to `render()` |
| 6.2 | `AbstractController::renderForm()` deprecated; use `render()` |
| 7.0 | `renderForm()` removed; pass the `FormInterface` to `render()`. Date and time types default `widget` to `single_text` and throw on model data in a different timezone |
| 7.4 docs | Passing `$form` (not `$form->createView()`) to `render()` sets HTTP 422 automatically |
| 8.1 | Placeholder of a required collapsed `ChoiceType` rendered with the `hidden` attribute; passing a boolean as the second argument of `ValidatorExtension` and `FormTypeValidatorExtension` constructors deprecated |

On 5.4 `createFormBuilder($task)` builds a form inline in a controller; `createForm()` takes a form class.

## Data Transformers

**What it is.** A pair of `transform()`/`reverseTransform()` methods converting a field value between representations; many field types (for example `DateType`) use them internally. Data has three formats: model (application), norm (usually the same as model) and view (form field). Model transformers convert model to norm and back; view transformers convert norm to view and back and are registered with `addViewTransformer()`.

**When to use.** One field whose form representation differs from the model value, for example an issue number typed as text and turned into an `Issue`. **When not to use.** Mapping several fields: the docs point to data mappers instead.

**Pitfalls.**
- Choose by the field's norm format: a `text` field's norm data is a string, so a model transformer fits.
- Attach to one field with `$builder->get('issue')->addModelTransformer($this->transformer)`. Chaining `addModelTransformer()` on the return value of `add()` applies the transformer to the entire form.
- `transform(null)` should return an equivalent empty value of the target type (`''`, `0`, `0.0`).
- Throw `TransformationFailedException` in `reverseTransform()` to cause a validation error. Its message is not shown to users; set the user-facing text with the `invalid_message` option, or call `setInvalidMessage()` on the exception for a public message with placeholders.
- Transformers are not applied to an `inherit_data` field.
- `CollectionType` creates children at `PRE_SET_DATA`, so a model transformer cannot reduce the number of items; use a DTO instead.
- `CallbackTransformer` is a shortcut taking two callbacks. For reuse, create a custom type whose `buildForm()` calls `addModelTransformer()` and whose `getParent()` returns `TextType::class`.
- With default autowiring and autoconfiguration the transformer is injected; otherwise register the form class as a service tagged `form.type`.

```php
public function transform($issue): string
{
    if (null === $issue) {
        return '';
    }

    return $issue->getId();
}

throw new TransformationFailedException(sprintf(
    'An issue with number "%s" does not exist!',
    $issueNumber
));
```

## Form Events

| Event | Data available | Typical use |
| --- | --- | --- |
| `PRE_SET_DATA` | Model data | Add or remove fields depending on whether the entity is new; can call `setData()` |
| `POST_SET_DATA` | Model data | Set data on unmapped children; adding fields in `PRE_SET_DATA` is preferred |
| `PRE_SUBMIT` | Request data | Sanitize input; add or remove fields based on submitted values; can call `setData()` |
| `SUBMIT` | Normalized data | Rare; a transformer is usually simpler; cannot add or remove fields |
| `POST_SUBMIT` | View data | Add fields to the parent form; add custom `FormError`s; validation runs here |

Submit order: `PRE_SUBMIT`, view-to-norm, `SUBMIT`, norm-to-model, `POST_SUBMIT` (validation).

**When to use.** Fields that depend on runtime data. Use listeners for simple form-specific logic and subscribers (`EventSubscriberInterface`, `addEventSubscriber()`) for logic reused across forms. **When not to use.** Static conditions (pass options), user-dependent data (inject Security or a repository), data conversion (transformers), custom mapping (data mappers or getter/setter), validation (constraints, validation groups or `When`), defaults (`empty_data`).

**Pitfalls.**
- Form events are per form instance and not part of the application-wide event system. A regular event subscriber in the container cannot listen to them; register all listeners in `buildForm()`.
- Never modify the form a listener is attached to during `POST_SUBMIT`; modify the parent.
- Fields added on render but not on submit cause "This form should not contain extra fields".
- Typed event classes are `PreSetDataEvent`, `PostSetDataEvent`, `PreSubmitEvent`, `SubmitEvent` and `PostSubmitEvent` in `Symfony\Component\Form\Event\`. Since 7.0 `PostSetDataEvent::setData()` and `PostSubmitEvent::setData()` throw; set data in `PRE_SET_DATA`, `PRE_SUBMIT` or `SUBMIT`.

```php
$builder->addEventListener(
    FormEvents::PRE_SET_DATA,
    function (PreSetDataEvent $event): void {
        $product = $event->getData();
        $form = $event->getForm();
        $isNew = !$product || null === $product->getId();

        if ($isNew) {
            $form->add('name', TextType::class);
        }
    }
);
```

## Collections

**What it is.** `CollectionType` with `entry_type` and `entry_options`. `allow_add` exposes a `prototype` variable (placeholder `__name__`) for client-side cloning; `allow_delete` removes on the server any item not sent on submission.

**When to use.** Editing a list of children inside one parent form.

**Pitfalls.**
- Without `allow_add`, extra submitted items fail with "This form should not contain extra fields". With `allow_delete`, remove the DOM element before submitting.
- `by_reference => false` makes the form call `addTag()`/`removeTag()`; both must exist, otherwise it uses `setTags()`. Pluralization to singular works only for English.
- On the inverse side, `addTag()` must set the owning side (`$tag->addTask($this)`), otherwise the relationship does not persist correctly.
- Without `cascade: ['persist']` on the association Doctrine fails with "A new entity was found through the relationship ... that was not configured to cascade persist operations". For removed items the docs point to Doctrine's `orphanRemoval` option.
- The collection field enables `error_bubbling` by default; set it to `false` to attach errors to the fields.
- Deeply nested forms can hit Xdebug's "Maximum function nesting level of '100' reached"; raise `xdebug.max_nesting_level` or render with `form_row()`.

## Multi-Step Form Flows

**What it is.** A flow is a custom form type extending `AbstractFlowType` with `buildFormFlow()`; steps are declared with `addStep()`, ordered by descending `priority`, and can be skipped with a `skip` callable. Validation groups are scoped to the current step (default `['Default', '<current_step_name>']`); the current step is stored on the data through `step_property_path`.

**Pitfalls.** Data storage defaults to `SessionDataStorage`, which needs a session; `InMemoryDataStorage` suits tests and `NullDataStorage` stores nothing. Nested flows are unsupported, and one step is processed per request.

**Versions.** Navigation buttons are `PreviousFlowType`, `NextFlowType`, `FinishFlowType` and `ResetFlowType`, bundled by `NavigatorFlowType`. Its `with_reset` option and the `form_flow_*()` Twig functions arrived in 8.1.

## Request Payload Mapping

**What it is.** Controller argument attributes backed by `RequestPayloadValueResolver` (6.3+). `#[MapRequestPayload]` maps the request payload, for example JSON in POST/PUT, onto a DTO with constraints. `#[MapQueryString]` maps the whole query string onto a DTO. `#[MapQueryParameter]` maps single parameters of type `\BackedEnum`, `array`, `bool`, `float`, `int`, `string` or an `AbstractUid` subclass, with an optional `filter:` taking PHP validate-filter constants.

**Pitfalls.**
- A validation failure returns 422 for `MapRequestPayload` and 404 for `MapQueryString`; change it with `validationFailedStatusCode` (for example `Response::HTTP_UNPROCESSABLE_ENTITY`).
- For JSON APIs declare the route with `format: 'json'` so validation errors are returned as JSON.
- Options: `acceptFormat`, `validationGroups`, `serializationContext`, `resolver` (payload); `validationGroups`, `key` (query string).

**Versions.** 8.1 adds `mapWhenEmpty: true` for `MapQueryString`, expressions in `validationGroups`, variadic arguments and multipart mapping.

```php
public function dashboard(#[MapRequestPayload] UserDto $userDto): Response
```

## Validator Constraints

**What it is.** Constraints (rules) checked by validators (logic classes) before data is written to the database or passed to a web service. Constraints go on properties and getters (`get`, `is`, `has`, any visibility) or on classes (for example `Callback`), as attributes, YAML/XML in `config/validator/`, or `loadValidatorMetadata()`. `ValidatorInterface::validate()` returns a `ConstraintViolationList`, empty when valid; `findByCodes()` filters it. `Validation::createCallable()` throws `ValidationFailedException`; `Validation::createIsValidCallable()` returns false.

**Pitfalls.**
- Adding constraints alone does not enforce them; the object must be passed to the validator.
- Embedded objects are validated only with `#[Assert\Valid]`; otherwise an author with an invalid address validates successfully. Arrays are always traversed (keys are not validated); `traverse` applies to `\Traversable`. Add `Type` to check the nested object's class too.
- An uninitialized typed property is validated as `null`; initialize all properties before validating.
- Parent property constraints always apply to child classes; use different groups to avoid that.
- `Sequentially` stops at the first violation, which avoids `Length`/`Regex` failing on non-strings, duplicate messages and expensive calls after a format failure.
- `When` applies `constraints` only if `expression` is true and `otherwise` when false; falsey results (`false`, `null`, `0`, `''`, `[]`) count as false. Variables: `this`, `value`, `context`. A closure as `expression` requires PHP 8.5.
- `Compound` is extended into a named, reusable set by overriding `getConstraints(array $options): array`.
- `AtLeastOneOf` passes when one constraint is satisfied and stops there.
- Doctrine validation auto mapping derives `NotNull`, `Type`, `UniqueEntity` and `Length` from column mapping but does not replace validation configuration.
- Inspect metadata with `php bin/console debug:validator 'App\Entity\SomeClass'`; metadata is cached when `kernel.debug` is false.

```php
#[Assert\NotBlank]
#[Assert\Length(min: 3)]
private string $firstName;

#[Assert\Valid]
protected Address $address;
```

**Versions.**

| Version | Change |
| --- | --- |
| 5.1 | `Sequentially` |
| 5.4 | `#[Sequentially]` attribute; nested attributes need PHP 8.1. Install is `symfony/validator doctrine/annotations`; annotations (`@Assert\NotBlank`) and attributes both documented |
| 6.2 | `loose` email validation mode deprecated |
| 6.4 | Doctrine annotations support deprecated; `enableAnnotationMapping()` replaced by `enableAttributeMapping()` |
| 7.0 | Doctrine annotations removed; `AnnotationLoader` replaced by `AttributeLoader`; `ERROR_NAMES` replaces `$errorNames`; `ExpressionSyntax` replaces `ExpressionLanguageSyntax` |
| 7.3 | Passing an options array to constraint constructors deprecated; use named arguments, e.g. `new NotNull(groups: [...], message: ...)` |
| 7.4 | `#[ExtendsValidationFor(Product::class)]` adds constraints to a class you cannot modify (missing properties throw `MappingException`); JSON schema for mapping files |
| 8.1 | `ConstraintValidatorInterface::initialize()`/`validate()` deprecated in favor of `validateInContext()`; implementing `ConstraintViolationListInterface` without `findByCodes()` deprecated |

## Custom Constraints

**What it is.** A class extending `Constraint` with `#[\Attribute]`, plus a validator extending `ConstraintValidator`, found by default as `static::class.'Validator'`. With the default `services.yaml` validators are tagged `validator.constraint_validator`, so constructor injection works. For a reusable set of built-ins, extend `Compound` instead.

**Pitfalls.**
- Pass all options to the constructor and call `parent::__construct(null, $groups, $payload)`.
- Constraints are cached via `get_object_vars`; list private properties in `__sleep()`.
- Throw `UnexpectedTypeException` for a wrong constraint class, return on `null` and `''` so `NotBlank` and `NotNull` handle them, and throw `UnexpectedValueException` for unsupported value types.
- For a class constraint return `self::CLASS_CONSTRAINT` from `getTargets()` and attach the violation to a property with `atPath()`.
- Test with `ConstraintValidatorTestCase`, `createValidator()` and `assertNoViolation()`.

```php
public function validate(mixed $value, Constraint $constraint): void
{
    if (!$constraint instanceof ContainsAlphanumeric) {
        throw new UnexpectedTypeException($constraint, ContainsAlphanumeric::class);
    }

    if (null === $value || '' === $value) {
        return;
    }

    $this->context->buildViolation($constraint->message)
        ->setParameter('{{ string }}', $value)
        ->addViolation();
}
```

**Versions.** `#[HasNamedArguments]` (6.1+) makes constructor options required; 7.3 deprecates custom constraints that do not support named arguments. `disableTranslation()` on the violation builder arrived in 6.4. 7.0 adds `getConstraint()`, `getCause()` and `__toString()` to `ConstraintViolationInterface`.

## Groups and Sequences

**What it is.** Without groups only `Default` is validated. `Default` holds constraints with no explicit group or with the class-name group. `$validator->validate($author, null, ['registration'])` runs only that group. A group sequence moves to the next group only if the current one passes.

**When to use.** Different rules per use case, or ordering checks so later groups run only after earlier ones pass. **When not to use.** A single property needing ordered checks: `Sequentially` is simpler.

**Pitfalls.**
- A constraint with `groups: ['registration']` belongs only to that group, not to `Default`.
- The class-name group and `Default` behave the same for a standalone object but differ for a `Valid` embedded object.
- Validating with a subclass name runs subclass and base constraints; the base class name runs only base default constraints.
- Never list `Default` in a sequence; it causes infinite recursion. Use the class name.
- `Valid` does not use `Default`: it is always applied, even when another group is requested, unless you set `groups`.
- In forms pass `'validation_groups' => new GroupSequence(['First', 'Second'])`.
- `GroupSequenceProvider`: implement `GroupSequenceProviderInterface::getGroupSequence()` and flag the class with `#[Assert\GroupSequenceProvider]`. A flat array stops at the first failing group; nested arrays validate all groups in each sub-array. A separate provider class uses `provider:` and `GroupProviderInterface`, tagged `validator.group_provider` without autowiring.

```php
#[Assert\GroupSequence(['User', 'Strict'])]
final class User implements UserInterface
{
    #[Assert\Email(groups: ['registration'])]
    private string $email;
}
```

## Sources

- https://symfony.com/doc/7.4/forms.html
- https://symfony.com/doc/5.4/forms.html
- https://symfony.com/doc/current/form/data_transformers.html
- https://symfony.com/doc/current/form/events.html
- https://symfony.com/doc/current/form/form_collections.html
- https://symfony.com/doc/current/form/form_flow.html
- https://symfony.com/doc/6.4/controller/value_resolver.html
- https://symfony.com/doc/current/controller.html
- https://symfony.com/doc/7.4/validation.html
- https://symfony.com/doc/5.4/validation.html
- https://symfony.com/doc/6.4/validation/custom_constraint.html
- https://symfony.com/doc/7.4/validation/sequence_provider.html
- https://symfony.com/doc/current/validation/groups.html
- https://symfony.com/doc/current/reference/constraints/Valid.html
- https://symfony.com/doc/current/reference/constraints/When.html
- https://symfony.com/doc/5.4/reference/constraints/Sequentially.html
- https://symfony.com/doc/current/reference/constraints/Compound.html
- https://symfony.com/doc/current/reference/constraints/AtLeastOneOf.html
- https://symfony.com/doc/7.4/doctrine.html
- https://github.com/symfony/symfony/blob/6.2/UPGRADE-6.2.md
- https://github.com/symfony/symfony/blob/6.4/UPGRADE-6.4.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
- https://github.com/symfony/symfony/blob/7.3/UPGRADE-7.3.md
- https://github.com/symfony/symfony/blob/8.1/UPGRADE-8.1.md
