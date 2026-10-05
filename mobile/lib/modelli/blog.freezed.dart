// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'blog.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$DomandaFaq {

 String get domanda; String get risposta;
/// Create a copy of DomandaFaq
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DomandaFaqCopyWith<DomandaFaq> get copyWith => _$DomandaFaqCopyWithImpl<DomandaFaq>(this as DomandaFaq, _$identity);

  /// Serializes this DomandaFaq to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as DomandaFaq;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DomandaFaq&&(identical(other.domanda, _this.domanda) || other.domanda == _this.domanda)&&(identical(other.risposta, _this.risposta) || other.risposta == _this.risposta));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as DomandaFaq;
  return Object.hash(runtimeType,_this.domanda,_this.risposta);
}

@override
String toString() {
  final _this = this as DomandaFaq;
  return 'DomandaFaq(domanda: ${_this.domanda}, risposta: ${_this.risposta})';
}


}

/// @nodoc
abstract mixin class $DomandaFaqCopyWith<$Res>  {
  factory $DomandaFaqCopyWith(DomandaFaq value, $Res Function(DomandaFaq) _then) = _$DomandaFaqCopyWithImpl;
@useResult
$Res call({
 String domanda, String risposta
});




}
/// @nodoc
class _$DomandaFaqCopyWithImpl<$Res>
    implements $DomandaFaqCopyWith<$Res> {
  _$DomandaFaqCopyWithImpl(this._self, this._then);

  final DomandaFaq _self;
  final $Res Function(DomandaFaq) _then;

/// Create a copy of DomandaFaq
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? domanda = null,Object? risposta = null,}) {
  return _then(DomandaFaq(
domanda: null == domanda ? _self.domanda : domanda // ignore: cast_nullable_to_non_nullable
as String,risposta: null == risposta ? _self.risposta : risposta // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [DomandaFaq].
extension DomandaFaqPatterns on DomandaFaq {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DomandaFaq value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DomandaFaq() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DomandaFaq value)  $default,){
final _that = this;
switch (_that) {
case _DomandaFaq():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DomandaFaq value)?  $default,){
final _that = this;
switch (_that) {
case _DomandaFaq() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String domanda,  String risposta)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DomandaFaq() when $default != null:
return $default(_that.domanda,_that.risposta);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String domanda,  String risposta)  $default,) {final _that = this;
switch (_that) {
case _DomandaFaq():
return $default(_that.domanda,_that.risposta);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String domanda,  String risposta)?  $default,) {final _that = this;
switch (_that) {
case _DomandaFaq() when $default != null:
return $default(_that.domanda,_that.risposta);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _DomandaFaq implements DomandaFaq {
  const _DomandaFaq({required this.domanda, required this.risposta});
  factory _DomandaFaq.fromJson(Map<String, dynamic> json) => _$DomandaFaqFromJson(json);

@override final  String domanda;
@override final  String risposta;

/// Create a copy of DomandaFaq
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DomandaFaqCopyWith<_DomandaFaq> get copyWith => __$DomandaFaqCopyWithImpl<_DomandaFaq>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DomandaFaqToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _DomandaFaq&&(identical(other.domanda, domanda) || other.domanda == domanda)&&(identical(other.risposta, risposta) || other.risposta == risposta));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,domanda,risposta);
}

@override
String toString() {
    return 'DomandaFaq(domanda: $domanda, risposta: $risposta)';
}


}

/// @nodoc
abstract mixin class _$DomandaFaqCopyWith<$Res> implements $DomandaFaqCopyWith<$Res> {
  factory _$DomandaFaqCopyWith(_DomandaFaq value, $Res Function(_DomandaFaq) _then) = __$DomandaFaqCopyWithImpl;
@override @useResult
$Res call({
 String domanda, String risposta
});




}
/// @nodoc
class __$DomandaFaqCopyWithImpl<$Res>
    implements _$DomandaFaqCopyWith<$Res> {
  __$DomandaFaqCopyWithImpl(this._self, this._then);

  final _DomandaFaq _self;
  final $Res Function(_DomandaFaq) _then;

/// Create a copy of DomandaFaq
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? domanda = null,Object? risposta = null,}) {
  return _then(_DomandaFaq(
domanda: null == domanda ? _self.domanda : domanda // ignore: cast_nullable_to_non_nullable
as String,risposta: null == risposta ? _self.risposta : risposta // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$CartaCitata {

 String get id; String get nomeIt; String get nome; String get slug; Map<String, String> get slugs;
/// Create a copy of CartaCitata
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CartaCitataCopyWith<CartaCitata> get copyWith => _$CartaCitataCopyWithImpl<CartaCitata>(this as CartaCitata, _$identity);

  /// Serializes this CartaCitata to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as CartaCitata;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CartaCitata&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.nomeIt, _this.nomeIt) || other.nomeIt == _this.nomeIt)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&const DeepCollectionEquality().equals(other.slugs, _this.slugs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as CartaCitata;
  return Object.hash(runtimeType,_this.id,_this.nomeIt,_this.nome,_this.slug,const DeepCollectionEquality().hash(_this.slugs));
}

@override
String toString() {
  final _this = this as CartaCitata;
  return 'CartaCitata(id: ${_this.id}, nomeIt: ${_this.nomeIt}, nome: ${_this.nome}, slug: ${_this.slug}, slugs: ${_this.slugs})';
}


}

/// @nodoc
abstract mixin class $CartaCitataCopyWith<$Res>  {
  factory $CartaCitataCopyWith(CartaCitata value, $Res Function(CartaCitata) _then) = _$CartaCitataCopyWithImpl;
@useResult
$Res call({
 String id, String nomeIt, String nome, String slug, Map<String, String> slugs
});




}
/// @nodoc
class _$CartaCitataCopyWithImpl<$Res>
    implements $CartaCitataCopyWith<$Res> {
  _$CartaCitataCopyWithImpl(this._self, this._then);

  final CartaCitata _self;
  final $Res Function(CartaCitata) _then;

/// Create a copy of CartaCitata
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nomeIt = null,Object? nome = null,Object? slug = null,Object? slugs = null,}) {
  return _then(CartaCitata(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nomeIt: null == nomeIt ? _self.nomeIt : nomeIt // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,slugs: null == slugs ? _self.slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,
  ));
}

}


/// Adds pattern-matching-related methods to [CartaCitata].
extension CartaCitataPatterns on CartaCitata {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CartaCitata value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CartaCitata() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CartaCitata value)  $default,){
final _that = this;
switch (_that) {
case _CartaCitata():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CartaCitata value)?  $default,){
final _that = this;
switch (_that) {
case _CartaCitata() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String nomeIt,  String nome,  String slug,  Map<String, String> slugs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CartaCitata() when $default != null:
return $default(_that.id,_that.nomeIt,_that.nome,_that.slug,_that.slugs);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String nomeIt,  String nome,  String slug,  Map<String, String> slugs)  $default,) {final _that = this;
switch (_that) {
case _CartaCitata():
return $default(_that.id,_that.nomeIt,_that.nome,_that.slug,_that.slugs);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String nomeIt,  String nome,  String slug,  Map<String, String> slugs)?  $default,) {final _that = this;
switch (_that) {
case _CartaCitata() when $default != null:
return $default(_that.id,_that.nomeIt,_that.nome,_that.slug,_that.slugs);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CartaCitata implements CartaCitata {
  const _CartaCitata({required this.id, this.nomeIt = '', required this.nome, required this.slug,  Map<String, String> slugs = const <String, String>{}}): _slugs = slugs;
  factory _CartaCitata.fromJson(Map<String, dynamic> json) => _$CartaCitataFromJson(json);

@override final  String id;
@override@JsonKey() final  String nomeIt;
@override final  String nome;
@override final  String slug;
 final  Map<String, String> _slugs;
@override@JsonKey() Map<String, String> get slugs {
  if (_slugs is EqualUnmodifiableMapView) return _slugs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_slugs);
}


/// Create a copy of CartaCitata
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CartaCitataCopyWith<_CartaCitata> get copyWith => __$CartaCitataCopyWithImpl<_CartaCitata>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CartaCitataToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _CartaCitata&&(identical(other.id, id) || other.id == id)&&(identical(other.nomeIt, nomeIt) || other.nomeIt == nomeIt)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.slug, slug) || other.slug == slug)&&const DeepCollectionEquality().equals(other.slugs, _slugs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,nomeIt,nome,slug,const DeepCollectionEquality().hash(_slugs));
}

@override
String toString() {
    return 'CartaCitata(id: $id, nomeIt: $nomeIt, nome: $nome, slug: $slug, slugs: $slugs)';
}


}

/// @nodoc
abstract mixin class _$CartaCitataCopyWith<$Res> implements $CartaCitataCopyWith<$Res> {
  factory _$CartaCitataCopyWith(_CartaCitata value, $Res Function(_CartaCitata) _then) = __$CartaCitataCopyWithImpl;
@override @useResult
$Res call({
 String id, String nomeIt, String nome, String slug, Map<String, String> slugs
});




}
/// @nodoc
class __$CartaCitataCopyWithImpl<$Res>
    implements _$CartaCitataCopyWith<$Res> {
  __$CartaCitataCopyWithImpl(this._self, this._then);

  final _CartaCitata _self;
  final $Res Function(_CartaCitata) _then;

/// Create a copy of CartaCitata
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nomeIt = null,Object? nome = null,Object? slug = null,Object? slugs = null,}) {
  return _then(_CartaCitata(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nomeIt: null == nomeIt ? _self.nomeIt : nomeIt // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,slugs: null == slugs ? _self._slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,
  ));
}


}


/// @nodoc
mixin _$StesaCitata {

 String get id; String get nome; String get slug; Map<String, String> get slugs;
/// Create a copy of StesaCitata
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StesaCitataCopyWith<StesaCitata> get copyWith => _$StesaCitataCopyWithImpl<StesaCitata>(this as StesaCitata, _$identity);

  /// Serializes this StesaCitata to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as StesaCitata;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StesaCitata&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&const DeepCollectionEquality().equals(other.slugs, _this.slugs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as StesaCitata;
  return Object.hash(runtimeType,_this.id,_this.nome,_this.slug,const DeepCollectionEquality().hash(_this.slugs));
}

@override
String toString() {
  final _this = this as StesaCitata;
  return 'StesaCitata(id: ${_this.id}, nome: ${_this.nome}, slug: ${_this.slug}, slugs: ${_this.slugs})';
}


}

/// @nodoc
abstract mixin class $StesaCitataCopyWith<$Res>  {
  factory $StesaCitataCopyWith(StesaCitata value, $Res Function(StesaCitata) _then) = _$StesaCitataCopyWithImpl;
@useResult
$Res call({
 String id, String nome, String slug, Map<String, String> slugs
});




}
/// @nodoc
class _$StesaCitataCopyWithImpl<$Res>
    implements $StesaCitataCopyWith<$Res> {
  _$StesaCitataCopyWithImpl(this._self, this._then);

  final StesaCitata _self;
  final $Res Function(StesaCitata) _then;

/// Create a copy of StesaCitata
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nome = null,Object? slug = null,Object? slugs = null,}) {
  return _then(StesaCitata(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,slugs: null == slugs ? _self.slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,
  ));
}

}


/// Adds pattern-matching-related methods to [StesaCitata].
extension StesaCitataPatterns on StesaCitata {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StesaCitata value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StesaCitata() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StesaCitata value)  $default,){
final _that = this;
switch (_that) {
case _StesaCitata():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StesaCitata value)?  $default,){
final _that = this;
switch (_that) {
case _StesaCitata() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String nome,  String slug,  Map<String, String> slugs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StesaCitata() when $default != null:
return $default(_that.id,_that.nome,_that.slug,_that.slugs);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String nome,  String slug,  Map<String, String> slugs)  $default,) {final _that = this;
switch (_that) {
case _StesaCitata():
return $default(_that.id,_that.nome,_that.slug,_that.slugs);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String nome,  String slug,  Map<String, String> slugs)?  $default,) {final _that = this;
switch (_that) {
case _StesaCitata() when $default != null:
return $default(_that.id,_that.nome,_that.slug,_that.slugs);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StesaCitata implements StesaCitata {
  const _StesaCitata({required this.id, required this.nome, required this.slug,  Map<String, String> slugs = const <String, String>{}}): _slugs = slugs;
  factory _StesaCitata.fromJson(Map<String, dynamic> json) => _$StesaCitataFromJson(json);

@override final  String id;
@override final  String nome;
@override final  String slug;
 final  Map<String, String> _slugs;
@override@JsonKey() Map<String, String> get slugs {
  if (_slugs is EqualUnmodifiableMapView) return _slugs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_slugs);
}


/// Create a copy of StesaCitata
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StesaCitataCopyWith<_StesaCitata> get copyWith => __$StesaCitataCopyWithImpl<_StesaCitata>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StesaCitataToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _StesaCitata&&(identical(other.id, id) || other.id == id)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.slug, slug) || other.slug == slug)&&const DeepCollectionEquality().equals(other.slugs, _slugs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,nome,slug,const DeepCollectionEquality().hash(_slugs));
}

@override
String toString() {
    return 'StesaCitata(id: $id, nome: $nome, slug: $slug, slugs: $slugs)';
}


}

/// @nodoc
abstract mixin class _$StesaCitataCopyWith<$Res> implements $StesaCitataCopyWith<$Res> {
  factory _$StesaCitataCopyWith(_StesaCitata value, $Res Function(_StesaCitata) _then) = __$StesaCitataCopyWithImpl;
@override @useResult
$Res call({
 String id, String nome, String slug, Map<String, String> slugs
});




}
/// @nodoc
class __$StesaCitataCopyWithImpl<$Res>
    implements _$StesaCitataCopyWith<$Res> {
  __$StesaCitataCopyWithImpl(this._self, this._then);

  final _StesaCitata _self;
  final $Res Function(_StesaCitata) _then;

/// Create a copy of StesaCitata
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nome = null,Object? slug = null,Object? slugs = null,}) {
  return _then(_StesaCitata(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,slugs: null == slugs ? _self._slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,
  ));
}


}


/// @nodoc
mixin _$Collegamenti {

 List<CartaCitata> get carte; List<StesaCitata> get stese; List<ArticoloBreve> get articoli;
/// Create a copy of Collegamenti
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CollegamentiCopyWith<Collegamenti> get copyWith => _$CollegamentiCopyWithImpl<Collegamenti>(this as Collegamenti, _$identity);

  /// Serializes this Collegamenti to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Collegamenti;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Collegamenti&&const DeepCollectionEquality().equals(other.carte, _this.carte)&&const DeepCollectionEquality().equals(other.stese, _this.stese)&&const DeepCollectionEquality().equals(other.articoli, _this.articoli));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Collegamenti;
  return Object.hash(runtimeType,const DeepCollectionEquality().hash(_this.carte),const DeepCollectionEquality().hash(_this.stese),const DeepCollectionEquality().hash(_this.articoli));
}

@override
String toString() {
  final _this = this as Collegamenti;
  return 'Collegamenti(carte: ${_this.carte}, stese: ${_this.stese}, articoli: ${_this.articoli})';
}


}

/// @nodoc
abstract mixin class $CollegamentiCopyWith<$Res>  {
  factory $CollegamentiCopyWith(Collegamenti value, $Res Function(Collegamenti) _then) = _$CollegamentiCopyWithImpl;
@useResult
$Res call({
 List<CartaCitata> carte, List<StesaCitata> stese, List<ArticoloBreve> articoli
});




}
/// @nodoc
class _$CollegamentiCopyWithImpl<$Res>
    implements $CollegamentiCopyWith<$Res> {
  _$CollegamentiCopyWithImpl(this._self, this._then);

  final Collegamenti _self;
  final $Res Function(Collegamenti) _then;

/// Create a copy of Collegamenti
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? carte = null,Object? stese = null,Object? articoli = null,}) {
  return _then(Collegamenti(
carte: null == carte ? _self.carte : carte // ignore: cast_nullable_to_non_nullable
as List<CartaCitata>,stese: null == stese ? _self.stese : stese // ignore: cast_nullable_to_non_nullable
as List<StesaCitata>,articoli: null == articoli ? _self.articoli : articoli // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,
  ));
}

}


/// Adds pattern-matching-related methods to [Collegamenti].
extension CollegamentiPatterns on Collegamenti {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Collegamenti value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Collegamenti() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Collegamenti value)  $default,){
final _that = this;
switch (_that) {
case _Collegamenti():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Collegamenti value)?  $default,){
final _that = this;
switch (_that) {
case _Collegamenti() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<CartaCitata> carte,  List<StesaCitata> stese,  List<ArticoloBreve> articoli)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Collegamenti() when $default != null:
return $default(_that.carte,_that.stese,_that.articoli);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<CartaCitata> carte,  List<StesaCitata> stese,  List<ArticoloBreve> articoli)  $default,) {final _that = this;
switch (_that) {
case _Collegamenti():
return $default(_that.carte,_that.stese,_that.articoli);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<CartaCitata> carte,  List<StesaCitata> stese,  List<ArticoloBreve> articoli)?  $default,) {final _that = this;
switch (_that) {
case _Collegamenti() when $default != null:
return $default(_that.carte,_that.stese,_that.articoli);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Collegamenti implements Collegamenti {
  const _Collegamenti({ List<CartaCitata> carte = const <CartaCitata>[],  List<StesaCitata> stese = const <StesaCitata>[],  List<ArticoloBreve> articoli = const <ArticoloBreve>[]}): _carte = carte,_stese = stese,_articoli = articoli;
  factory _Collegamenti.fromJson(Map<String, dynamic> json) => _$CollegamentiFromJson(json);

 final  List<CartaCitata> _carte;
@override@JsonKey() List<CartaCitata> get carte {
  if (_carte is EqualUnmodifiableListView) return _carte;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_carte);
}

 final  List<StesaCitata> _stese;
@override@JsonKey() List<StesaCitata> get stese {
  if (_stese is EqualUnmodifiableListView) return _stese;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_stese);
}

 final  List<ArticoloBreve> _articoli;
@override@JsonKey() List<ArticoloBreve> get articoli {
  if (_articoli is EqualUnmodifiableListView) return _articoli;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_articoli);
}


/// Create a copy of Collegamenti
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CollegamentiCopyWith<_Collegamenti> get copyWith => __$CollegamentiCopyWithImpl<_Collegamenti>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CollegamentiToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Collegamenti&&const DeepCollectionEquality().equals(other.carte, _carte)&&const DeepCollectionEquality().equals(other.stese, _stese)&&const DeepCollectionEquality().equals(other.articoli, _articoli));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,const DeepCollectionEquality().hash(_carte),const DeepCollectionEquality().hash(_stese),const DeepCollectionEquality().hash(_articoli));
}

@override
String toString() {
    return 'Collegamenti(carte: $carte, stese: $stese, articoli: $articoli)';
}


}

/// @nodoc
abstract mixin class _$CollegamentiCopyWith<$Res> implements $CollegamentiCopyWith<$Res> {
  factory _$CollegamentiCopyWith(_Collegamenti value, $Res Function(_Collegamenti) _then) = __$CollegamentiCopyWithImpl;
@override @useResult
$Res call({
 List<CartaCitata> carte, List<StesaCitata> stese, List<ArticoloBreve> articoli
});




}
/// @nodoc
class __$CollegamentiCopyWithImpl<$Res>
    implements _$CollegamentiCopyWith<$Res> {
  __$CollegamentiCopyWithImpl(this._self, this._then);

  final _Collegamenti _self;
  final $Res Function(_Collegamenti) _then;

/// Create a copy of Collegamenti
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? carte = null,Object? stese = null,Object? articoli = null,}) {
  return _then(_Collegamenti(
carte: null == carte ? _self._carte : carte // ignore: cast_nullable_to_non_nullable
as List<CartaCitata>,stese: null == stese ? _self._stese : stese // ignore: cast_nullable_to_non_nullable
as List<StesaCitata>,articoli: null == articoli ? _self._articoli : articoli // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,
  ));
}


}


/// @nodoc
mixin _$Gemella {

 String get lang; String get slug;
/// Create a copy of Gemella
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GemellaCopyWith<Gemella> get copyWith => _$GemellaCopyWithImpl<Gemella>(this as Gemella, _$identity);

  /// Serializes this Gemella to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Gemella;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Gemella&&(identical(other.lang, _this.lang) || other.lang == _this.lang)&&(identical(other.slug, _this.slug) || other.slug == _this.slug));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Gemella;
  return Object.hash(runtimeType,_this.lang,_this.slug);
}

@override
String toString() {
  final _this = this as Gemella;
  return 'Gemella(lang: ${_this.lang}, slug: ${_this.slug})';
}


}

/// @nodoc
abstract mixin class $GemellaCopyWith<$Res>  {
  factory $GemellaCopyWith(Gemella value, $Res Function(Gemella) _then) = _$GemellaCopyWithImpl;
@useResult
$Res call({
 String lang, String slug
});




}
/// @nodoc
class _$GemellaCopyWithImpl<$Res>
    implements $GemellaCopyWith<$Res> {
  _$GemellaCopyWithImpl(this._self, this._then);

  final Gemella _self;
  final $Res Function(Gemella) _then;

/// Create a copy of Gemella
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? lang = null,Object? slug = null,}) {
  return _then(Gemella(
lang: null == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [Gemella].
extension GemellaPatterns on Gemella {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Gemella value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Gemella() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Gemella value)  $default,){
final _that = this;
switch (_that) {
case _Gemella():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Gemella value)?  $default,){
final _that = this;
switch (_that) {
case _Gemella() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String lang,  String slug)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Gemella() when $default != null:
return $default(_that.lang,_that.slug);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String lang,  String slug)  $default,) {final _that = this;
switch (_that) {
case _Gemella():
return $default(_that.lang,_that.slug);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String lang,  String slug)?  $default,) {final _that = this;
switch (_that) {
case _Gemella() when $default != null:
return $default(_that.lang,_that.slug);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Gemella implements Gemella {
  const _Gemella({required this.lang, required this.slug});
  factory _Gemella.fromJson(Map<String, dynamic> json) => _$GemellaFromJson(json);

@override final  String lang;
@override final  String slug;

/// Create a copy of Gemella
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$GemellaCopyWith<_Gemella> get copyWith => __$GemellaCopyWithImpl<_Gemella>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$GemellaToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Gemella&&(identical(other.lang, lang) || other.lang == lang)&&(identical(other.slug, slug) || other.slug == slug));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,lang,slug);
}

@override
String toString() {
    return 'Gemella(lang: $lang, slug: $slug)';
}


}

/// @nodoc
abstract mixin class _$GemellaCopyWith<$Res> implements $GemellaCopyWith<$Res> {
  factory _$GemellaCopyWith(_Gemella value, $Res Function(_Gemella) _then) = __$GemellaCopyWithImpl;
@override @useResult
$Res call({
 String lang, String slug
});




}
/// @nodoc
class __$GemellaCopyWithImpl<$Res>
    implements _$GemellaCopyWith<$Res> {
  __$GemellaCopyWithImpl(this._self, this._then);

  final _Gemella _self;
  final $Res Function(_Gemella) _then;

/// Create a copy of Gemella
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? lang = null,Object? slug = null,}) {
  return _then(_Gemella(
lang: null == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$ArticoloBlog {

 String get slug; String get titolo; String? get sottotitolo; String get estratto; ImmagineArticolo? get immagine; Voce? get sezione; AutoreBlog? get autore; String? get pubblicatoIl; String? get aggiornatoIl; int get tempoLettura; List<Voce> get tags; String get lang; bool get inEvidenza; String get testo; String? get seoTitolo; String get seoDescrizione; List<DomandaFaq> get faq; bool get commentiAperti; List<Voce> get briciole; Collegamenti get collegamenti; List<ArticoloBreve> get correlati; ArticoloBreve? get precedente; ArticoloBreve? get successivo; Gemella? get gemellaLingua;/// La carta o la stesa di cui parla (v9.4), o null.
 SoggettoArticolo? get soggetto;
/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ArticoloBlogCopyWith<ArticoloBlog> get copyWith => _$ArticoloBlogCopyWithImpl<ArticoloBlog>(this as ArticoloBlog, _$identity);

  /// Serializes this ArticoloBlog to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ArticoloBlog;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ArticoloBlog&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&(identical(other.titolo, _this.titolo) || other.titolo == _this.titolo)&&(identical(other.sottotitolo, _this.sottotitolo) || other.sottotitolo == _this.sottotitolo)&&(identical(other.estratto, _this.estratto) || other.estratto == _this.estratto)&&(identical(other.immagine, _this.immagine) || other.immagine == _this.immagine)&&(identical(other.sezione, _this.sezione) || other.sezione == _this.sezione)&&(identical(other.autore, _this.autore) || other.autore == _this.autore)&&(identical(other.pubblicatoIl, _this.pubblicatoIl) || other.pubblicatoIl == _this.pubblicatoIl)&&(identical(other.aggiornatoIl, _this.aggiornatoIl) || other.aggiornatoIl == _this.aggiornatoIl)&&(identical(other.tempoLettura, _this.tempoLettura) || other.tempoLettura == _this.tempoLettura)&&const DeepCollectionEquality().equals(other.tags, _this.tags)&&(identical(other.lang, _this.lang) || other.lang == _this.lang)&&(identical(other.inEvidenza, _this.inEvidenza) || other.inEvidenza == _this.inEvidenza)&&(identical(other.testo, _this.testo) || other.testo == _this.testo)&&(identical(other.seoTitolo, _this.seoTitolo) || other.seoTitolo == _this.seoTitolo)&&(identical(other.seoDescrizione, _this.seoDescrizione) || other.seoDescrizione == _this.seoDescrizione)&&const DeepCollectionEquality().equals(other.faq, _this.faq)&&(identical(other.commentiAperti, _this.commentiAperti) || other.commentiAperti == _this.commentiAperti)&&const DeepCollectionEquality().equals(other.briciole, _this.briciole)&&(identical(other.collegamenti, _this.collegamenti) || other.collegamenti == _this.collegamenti)&&const DeepCollectionEquality().equals(other.correlati, _this.correlati)&&(identical(other.precedente, _this.precedente) || other.precedente == _this.precedente)&&(identical(other.successivo, _this.successivo) || other.successivo == _this.successivo)&&(identical(other.gemellaLingua, _this.gemellaLingua) || other.gemellaLingua == _this.gemellaLingua)&&(identical(other.soggetto, _this.soggetto) || other.soggetto == _this.soggetto));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ArticoloBlog;
  return Object.hashAll([runtimeType,_this.slug,_this.titolo,_this.sottotitolo,_this.estratto,_this.immagine,_this.sezione,_this.autore,_this.pubblicatoIl,_this.aggiornatoIl,_this.tempoLettura,const DeepCollectionEquality().hash(_this.tags),_this.lang,_this.inEvidenza,_this.testo,_this.seoTitolo,_this.seoDescrizione,const DeepCollectionEquality().hash(_this.faq),_this.commentiAperti,const DeepCollectionEquality().hash(_this.briciole),_this.collegamenti,const DeepCollectionEquality().hash(_this.correlati),_this.precedente,_this.successivo,_this.gemellaLingua,_this.soggetto]);
}

@override
String toString() {
  final _this = this as ArticoloBlog;
  return 'ArticoloBlog(slug: ${_this.slug}, titolo: ${_this.titolo}, sottotitolo: ${_this.sottotitolo}, estratto: ${_this.estratto}, immagine: ${_this.immagine}, sezione: ${_this.sezione}, autore: ${_this.autore}, pubblicatoIl: ${_this.pubblicatoIl}, aggiornatoIl: ${_this.aggiornatoIl}, tempoLettura: ${_this.tempoLettura}, tags: ${_this.tags}, lang: ${_this.lang}, inEvidenza: ${_this.inEvidenza}, testo: ${_this.testo}, seoTitolo: ${_this.seoTitolo}, seoDescrizione: ${_this.seoDescrizione}, faq: ${_this.faq}, commentiAperti: ${_this.commentiAperti}, briciole: ${_this.briciole}, collegamenti: ${_this.collegamenti}, correlati: ${_this.correlati}, precedente: ${_this.precedente}, successivo: ${_this.successivo}, gemellaLingua: ${_this.gemellaLingua}, soggetto: ${_this.soggetto})';
}


}

/// @nodoc
abstract mixin class $ArticoloBlogCopyWith<$Res>  {
  factory $ArticoloBlogCopyWith(ArticoloBlog value, $Res Function(ArticoloBlog) _then) = _$ArticoloBlogCopyWithImpl;
@useResult
$Res call({
 String slug, String titolo, String? sottotitolo, String estratto, ImmagineArticolo? immagine, Voce? sezione, AutoreBlog? autore, String? pubblicatoIl, String? aggiornatoIl, int tempoLettura, List<Voce> tags, String lang, bool inEvidenza, String testo, String? seoTitolo, String seoDescrizione, List<DomandaFaq> faq, bool commentiAperti, List<Voce> briciole, Collegamenti collegamenti, List<ArticoloBreve> correlati, ArticoloBreve? precedente, ArticoloBreve? successivo, Gemella? gemellaLingua, SoggettoArticolo? soggetto
});


$ImmagineArticoloCopyWith<$Res>? get immagine;$VoceCopyWith<$Res>? get sezione;$AutoreBlogCopyWith<$Res>? get autore;$CollegamentiCopyWith<$Res> get collegamenti;$ArticoloBreveCopyWith<$Res>? get precedente;$ArticoloBreveCopyWith<$Res>? get successivo;$GemellaCopyWith<$Res>? get gemellaLingua;$SoggettoArticoloCopyWith<$Res>? get soggetto;

}
/// @nodoc
class _$ArticoloBlogCopyWithImpl<$Res>
    implements $ArticoloBlogCopyWith<$Res> {
  _$ArticoloBlogCopyWithImpl(this._self, this._then);

  final ArticoloBlog _self;
  final $Res Function(ArticoloBlog) _then;

/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? slug = null,Object? titolo = null,Object? sottotitolo = freezed,Object? estratto = null,Object? immagine = freezed,Object? sezione = freezed,Object? autore = freezed,Object? pubblicatoIl = freezed,Object? aggiornatoIl = freezed,Object? tempoLettura = null,Object? tags = null,Object? lang = null,Object? inEvidenza = null,Object? testo = null,Object? seoTitolo = freezed,Object? seoDescrizione = null,Object? faq = null,Object? commentiAperti = null,Object? briciole = null,Object? collegamenti = null,Object? correlati = null,Object? precedente = freezed,Object? successivo = freezed,Object? gemellaLingua = freezed,Object? soggetto = freezed,}) {
  return _then(ArticoloBlog(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,titolo: null == titolo ? _self.titolo : titolo // ignore: cast_nullable_to_non_nullable
as String,sottotitolo: freezed == sottotitolo ? _self.sottotitolo : sottotitolo // ignore: cast_nullable_to_non_nullable
as String?,estratto: null == estratto ? _self.estratto : estratto // ignore: cast_nullable_to_non_nullable
as String,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineArticolo?,sezione: freezed == sezione ? _self.sezione : sezione // ignore: cast_nullable_to_non_nullable
as Voce?,autore: freezed == autore ? _self.autore : autore // ignore: cast_nullable_to_non_nullable
as AutoreBlog?,pubblicatoIl: freezed == pubblicatoIl ? _self.pubblicatoIl : pubblicatoIl // ignore: cast_nullable_to_non_nullable
as String?,aggiornatoIl: freezed == aggiornatoIl ? _self.aggiornatoIl : aggiornatoIl // ignore: cast_nullable_to_non_nullable
as String?,tempoLettura: null == tempoLettura ? _self.tempoLettura : tempoLettura // ignore: cast_nullable_to_non_nullable
as int,tags: null == tags ? _self.tags : tags // ignore: cast_nullable_to_non_nullable
as List<Voce>,lang: null == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String,inEvidenza: null == inEvidenza ? _self.inEvidenza : inEvidenza // ignore: cast_nullable_to_non_nullable
as bool,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,seoTitolo: freezed == seoTitolo ? _self.seoTitolo : seoTitolo // ignore: cast_nullable_to_non_nullable
as String?,seoDescrizione: null == seoDescrizione ? _self.seoDescrizione : seoDescrizione // ignore: cast_nullable_to_non_nullable
as String,faq: null == faq ? _self.faq : faq // ignore: cast_nullable_to_non_nullable
as List<DomandaFaq>,commentiAperti: null == commentiAperti ? _self.commentiAperti : commentiAperti // ignore: cast_nullable_to_non_nullable
as bool,briciole: null == briciole ? _self.briciole : briciole // ignore: cast_nullable_to_non_nullable
as List<Voce>,collegamenti: null == collegamenti ? _self.collegamenti : collegamenti // ignore: cast_nullable_to_non_nullable
as Collegamenti,correlati: null == correlati ? _self.correlati : correlati // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,precedente: freezed == precedente ? _self.precedente : precedente // ignore: cast_nullable_to_non_nullable
as ArticoloBreve?,successivo: freezed == successivo ? _self.successivo : successivo // ignore: cast_nullable_to_non_nullable
as ArticoloBreve?,gemellaLingua: freezed == gemellaLingua ? _self.gemellaLingua : gemellaLingua // ignore: cast_nullable_to_non_nullable
as Gemella?,soggetto: freezed == soggetto ? _self.soggetto : soggetto // ignore: cast_nullable_to_non_nullable
as SoggettoArticolo?,
  ));
}
/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineArticoloCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineArticoloCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$VoceCopyWith<$Res>? get sezione {
    if (_self.sezione == null) {
    return null;
  }

  return $VoceCopyWith<$Res>(_self.sezione!, (value) {
    return _then(_self.copyWith(sezione: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AutoreBlogCopyWith<$Res>? get autore {
    if (_self.autore == null) {
    return null;
  }

  return $AutoreBlogCopyWith<$Res>(_self.autore!, (value) {
    return _then(_self.copyWith(autore: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CollegamentiCopyWith<$Res> get collegamenti {
  
  return $CollegamentiCopyWith<$Res>(_self.collegamenti, (value) {
    return _then(_self.copyWith(collegamenti: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ArticoloBreveCopyWith<$Res>? get precedente {
    if (_self.precedente == null) {
    return null;
  }

  return $ArticoloBreveCopyWith<$Res>(_self.precedente!, (value) {
    return _then(_self.copyWith(precedente: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ArticoloBreveCopyWith<$Res>? get successivo {
    if (_self.successivo == null) {
    return null;
  }

  return $ArticoloBreveCopyWith<$Res>(_self.successivo!, (value) {
    return _then(_self.copyWith(successivo: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GemellaCopyWith<$Res>? get gemellaLingua {
    if (_self.gemellaLingua == null) {
    return null;
  }

  return $GemellaCopyWith<$Res>(_self.gemellaLingua!, (value) {
    return _then(_self.copyWith(gemellaLingua: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SoggettoArticoloCopyWith<$Res>? get soggetto {
    if (_self.soggetto == null) {
    return null;
  }

  return $SoggettoArticoloCopyWith<$Res>(_self.soggetto!, (value) {
    return _then(_self.copyWith(soggetto: value));
  });
}
}


/// Adds pattern-matching-related methods to [ArticoloBlog].
extension ArticoloBlogPatterns on ArticoloBlog {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ArticoloBlog value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ArticoloBlog() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ArticoloBlog value)  $default,){
final _that = this;
switch (_that) {
case _ArticoloBlog():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ArticoloBlog value)?  $default,){
final _that = this;
switch (_that) {
case _ArticoloBlog() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String slug,  String titolo,  String? sottotitolo,  String estratto,  ImmagineArticolo? immagine,  Voce? sezione,  AutoreBlog? autore,  String? pubblicatoIl,  String? aggiornatoIl,  int tempoLettura,  List<Voce> tags,  String lang,  bool inEvidenza,  String testo,  String? seoTitolo,  String seoDescrizione,  List<DomandaFaq> faq,  bool commentiAperti,  List<Voce> briciole,  Collegamenti collegamenti,  List<ArticoloBreve> correlati,  ArticoloBreve? precedente,  ArticoloBreve? successivo,  Gemella? gemellaLingua,  SoggettoArticolo? soggetto)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ArticoloBlog() when $default != null:
return $default(_that.slug,_that.titolo,_that.sottotitolo,_that.estratto,_that.immagine,_that.sezione,_that.autore,_that.pubblicatoIl,_that.aggiornatoIl,_that.tempoLettura,_that.tags,_that.lang,_that.inEvidenza,_that.testo,_that.seoTitolo,_that.seoDescrizione,_that.faq,_that.commentiAperti,_that.briciole,_that.collegamenti,_that.correlati,_that.precedente,_that.successivo,_that.gemellaLingua,_that.soggetto);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String slug,  String titolo,  String? sottotitolo,  String estratto,  ImmagineArticolo? immagine,  Voce? sezione,  AutoreBlog? autore,  String? pubblicatoIl,  String? aggiornatoIl,  int tempoLettura,  List<Voce> tags,  String lang,  bool inEvidenza,  String testo,  String? seoTitolo,  String seoDescrizione,  List<DomandaFaq> faq,  bool commentiAperti,  List<Voce> briciole,  Collegamenti collegamenti,  List<ArticoloBreve> correlati,  ArticoloBreve? precedente,  ArticoloBreve? successivo,  Gemella? gemellaLingua,  SoggettoArticolo? soggetto)  $default,) {final _that = this;
switch (_that) {
case _ArticoloBlog():
return $default(_that.slug,_that.titolo,_that.sottotitolo,_that.estratto,_that.immagine,_that.sezione,_that.autore,_that.pubblicatoIl,_that.aggiornatoIl,_that.tempoLettura,_that.tags,_that.lang,_that.inEvidenza,_that.testo,_that.seoTitolo,_that.seoDescrizione,_that.faq,_that.commentiAperti,_that.briciole,_that.collegamenti,_that.correlati,_that.precedente,_that.successivo,_that.gemellaLingua,_that.soggetto);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String slug,  String titolo,  String? sottotitolo,  String estratto,  ImmagineArticolo? immagine,  Voce? sezione,  AutoreBlog? autore,  String? pubblicatoIl,  String? aggiornatoIl,  int tempoLettura,  List<Voce> tags,  String lang,  bool inEvidenza,  String testo,  String? seoTitolo,  String seoDescrizione,  List<DomandaFaq> faq,  bool commentiAperti,  List<Voce> briciole,  Collegamenti collegamenti,  List<ArticoloBreve> correlati,  ArticoloBreve? precedente,  ArticoloBreve? successivo,  Gemella? gemellaLingua,  SoggettoArticolo? soggetto)?  $default,) {final _that = this;
switch (_that) {
case _ArticoloBlog() when $default != null:
return $default(_that.slug,_that.titolo,_that.sottotitolo,_that.estratto,_that.immagine,_that.sezione,_that.autore,_that.pubblicatoIl,_that.aggiornatoIl,_that.tempoLettura,_that.tags,_that.lang,_that.inEvidenza,_that.testo,_that.seoTitolo,_that.seoDescrizione,_that.faq,_that.commentiAperti,_that.briciole,_that.collegamenti,_that.correlati,_that.precedente,_that.successivo,_that.gemellaLingua,_that.soggetto);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ArticoloBlog implements ArticoloBlog {
  const _ArticoloBlog({required this.slug, required this.titolo, this.sottotitolo, this.estratto = '', this.immagine, this.sezione, this.autore, this.pubblicatoIl, this.aggiornatoIl, this.tempoLettura = 1,  List<Voce> tags = const <Voce>[], this.lang = 'en', this.inEvidenza = false, this.testo = '', this.seoTitolo, this.seoDescrizione = '',  List<DomandaFaq> faq = const <DomandaFaq>[], this.commentiAperti = false,  List<Voce> briciole = const <Voce>[], this.collegamenti = const Collegamenti(),  List<ArticoloBreve> correlati = const <ArticoloBreve>[], this.precedente, this.successivo, this.gemellaLingua, this.soggetto}): _tags = tags,_faq = faq,_briciole = briciole,_correlati = correlati;
  factory _ArticoloBlog.fromJson(Map<String, dynamic> json) => _$ArticoloBlogFromJson(json);

@override final  String slug;
@override final  String titolo;
@override final  String? sottotitolo;
@override@JsonKey() final  String estratto;
@override final  ImmagineArticolo? immagine;
@override final  Voce? sezione;
@override final  AutoreBlog? autore;
@override final  String? pubblicatoIl;
@override final  String? aggiornatoIl;
@override@JsonKey() final  int tempoLettura;
 final  List<Voce> _tags;
@override@JsonKey() List<Voce> get tags {
  if (_tags is EqualUnmodifiableListView) return _tags;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_tags);
}

@override@JsonKey() final  String lang;
@override@JsonKey() final  bool inEvidenza;
@override@JsonKey() final  String testo;
@override final  String? seoTitolo;
@override@JsonKey() final  String seoDescrizione;
 final  List<DomandaFaq> _faq;
@override@JsonKey() List<DomandaFaq> get faq {
  if (_faq is EqualUnmodifiableListView) return _faq;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_faq);
}

@override@JsonKey() final  bool commentiAperti;
 final  List<Voce> _briciole;
@override@JsonKey() List<Voce> get briciole {
  if (_briciole is EqualUnmodifiableListView) return _briciole;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_briciole);
}

@override@JsonKey() final  Collegamenti collegamenti;
 final  List<ArticoloBreve> _correlati;
@override@JsonKey() List<ArticoloBreve> get correlati {
  if (_correlati is EqualUnmodifiableListView) return _correlati;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_correlati);
}

@override final  ArticoloBreve? precedente;
@override final  ArticoloBreve? successivo;
@override final  Gemella? gemellaLingua;
/// La carta o la stesa di cui parla (v9.4), o null.
@override final  SoggettoArticolo? soggetto;

/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ArticoloBlogCopyWith<_ArticoloBlog> get copyWith => __$ArticoloBlogCopyWithImpl<_ArticoloBlog>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ArticoloBlogToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ArticoloBlog&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.titolo, titolo) || other.titolo == titolo)&&(identical(other.sottotitolo, sottotitolo) || other.sottotitolo == sottotitolo)&&(identical(other.estratto, estratto) || other.estratto == estratto)&&(identical(other.immagine, immagine) || other.immagine == immagine)&&(identical(other.sezione, sezione) || other.sezione == sezione)&&(identical(other.autore, autore) || other.autore == autore)&&(identical(other.pubblicatoIl, pubblicatoIl) || other.pubblicatoIl == pubblicatoIl)&&(identical(other.aggiornatoIl, aggiornatoIl) || other.aggiornatoIl == aggiornatoIl)&&(identical(other.tempoLettura, tempoLettura) || other.tempoLettura == tempoLettura)&&const DeepCollectionEquality().equals(other.tags, _tags)&&(identical(other.lang, lang) || other.lang == lang)&&(identical(other.inEvidenza, inEvidenza) || other.inEvidenza == inEvidenza)&&(identical(other.testo, testo) || other.testo == testo)&&(identical(other.seoTitolo, seoTitolo) || other.seoTitolo == seoTitolo)&&(identical(other.seoDescrizione, seoDescrizione) || other.seoDescrizione == seoDescrizione)&&const DeepCollectionEquality().equals(other.faq, _faq)&&(identical(other.commentiAperti, commentiAperti) || other.commentiAperti == commentiAperti)&&const DeepCollectionEquality().equals(other.briciole, _briciole)&&(identical(other.collegamenti, collegamenti) || other.collegamenti == collegamenti)&&const DeepCollectionEquality().equals(other.correlati, _correlati)&&(identical(other.precedente, precedente) || other.precedente == precedente)&&(identical(other.successivo, successivo) || other.successivo == successivo)&&(identical(other.gemellaLingua, gemellaLingua) || other.gemellaLingua == gemellaLingua)&&(identical(other.soggetto, soggetto) || other.soggetto == soggetto));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,slug,titolo,sottotitolo,estratto,immagine,sezione,autore,pubblicatoIl,aggiornatoIl,tempoLettura,const DeepCollectionEquality().hash(_tags),lang,inEvidenza,testo,seoTitolo,seoDescrizione,const DeepCollectionEquality().hash(_faq),commentiAperti,const DeepCollectionEquality().hash(_briciole),collegamenti,const DeepCollectionEquality().hash(_correlati),precedente,successivo,gemellaLingua,soggetto]);
}

@override
String toString() {
    return 'ArticoloBlog(slug: $slug, titolo: $titolo, sottotitolo: $sottotitolo, estratto: $estratto, immagine: $immagine, sezione: $sezione, autore: $autore, pubblicatoIl: $pubblicatoIl, aggiornatoIl: $aggiornatoIl, tempoLettura: $tempoLettura, tags: $tags, lang: $lang, inEvidenza: $inEvidenza, testo: $testo, seoTitolo: $seoTitolo, seoDescrizione: $seoDescrizione, faq: $faq, commentiAperti: $commentiAperti, briciole: $briciole, collegamenti: $collegamenti, correlati: $correlati, precedente: $precedente, successivo: $successivo, gemellaLingua: $gemellaLingua, soggetto: $soggetto)';
}


}

/// @nodoc
abstract mixin class _$ArticoloBlogCopyWith<$Res> implements $ArticoloBlogCopyWith<$Res> {
  factory _$ArticoloBlogCopyWith(_ArticoloBlog value, $Res Function(_ArticoloBlog) _then) = __$ArticoloBlogCopyWithImpl;
@override @useResult
$Res call({
 String slug, String titolo, String? sottotitolo, String estratto, ImmagineArticolo? immagine, Voce? sezione, AutoreBlog? autore, String? pubblicatoIl, String? aggiornatoIl, int tempoLettura, List<Voce> tags, String lang, bool inEvidenza, String testo, String? seoTitolo, String seoDescrizione, List<DomandaFaq> faq, bool commentiAperti, List<Voce> briciole, Collegamenti collegamenti, List<ArticoloBreve> correlati, ArticoloBreve? precedente, ArticoloBreve? successivo, Gemella? gemellaLingua, SoggettoArticolo? soggetto
});


@override $ImmagineArticoloCopyWith<$Res>? get immagine;@override $VoceCopyWith<$Res>? get sezione;@override $AutoreBlogCopyWith<$Res>? get autore;@override $CollegamentiCopyWith<$Res> get collegamenti;@override $ArticoloBreveCopyWith<$Res>? get precedente;@override $ArticoloBreveCopyWith<$Res>? get successivo;@override $GemellaCopyWith<$Res>? get gemellaLingua;@override $SoggettoArticoloCopyWith<$Res>? get soggetto;

}
/// @nodoc
class __$ArticoloBlogCopyWithImpl<$Res>
    implements _$ArticoloBlogCopyWith<$Res> {
  __$ArticoloBlogCopyWithImpl(this._self, this._then);

  final _ArticoloBlog _self;
  final $Res Function(_ArticoloBlog) _then;

/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? slug = null,Object? titolo = null,Object? sottotitolo = freezed,Object? estratto = null,Object? immagine = freezed,Object? sezione = freezed,Object? autore = freezed,Object? pubblicatoIl = freezed,Object? aggiornatoIl = freezed,Object? tempoLettura = null,Object? tags = null,Object? lang = null,Object? inEvidenza = null,Object? testo = null,Object? seoTitolo = freezed,Object? seoDescrizione = null,Object? faq = null,Object? commentiAperti = null,Object? briciole = null,Object? collegamenti = null,Object? correlati = null,Object? precedente = freezed,Object? successivo = freezed,Object? gemellaLingua = freezed,Object? soggetto = freezed,}) {
  return _then(_ArticoloBlog(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,titolo: null == titolo ? _self.titolo : titolo // ignore: cast_nullable_to_non_nullable
as String,sottotitolo: freezed == sottotitolo ? _self.sottotitolo : sottotitolo // ignore: cast_nullable_to_non_nullable
as String?,estratto: null == estratto ? _self.estratto : estratto // ignore: cast_nullable_to_non_nullable
as String,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineArticolo?,sezione: freezed == sezione ? _self.sezione : sezione // ignore: cast_nullable_to_non_nullable
as Voce?,autore: freezed == autore ? _self.autore : autore // ignore: cast_nullable_to_non_nullable
as AutoreBlog?,pubblicatoIl: freezed == pubblicatoIl ? _self.pubblicatoIl : pubblicatoIl // ignore: cast_nullable_to_non_nullable
as String?,aggiornatoIl: freezed == aggiornatoIl ? _self.aggiornatoIl : aggiornatoIl // ignore: cast_nullable_to_non_nullable
as String?,tempoLettura: null == tempoLettura ? _self.tempoLettura : tempoLettura // ignore: cast_nullable_to_non_nullable
as int,tags: null == tags ? _self._tags : tags // ignore: cast_nullable_to_non_nullable
as List<Voce>,lang: null == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String,inEvidenza: null == inEvidenza ? _self.inEvidenza : inEvidenza // ignore: cast_nullable_to_non_nullable
as bool,testo: null == testo ? _self.testo : testo // ignore: cast_nullable_to_non_nullable
as String,seoTitolo: freezed == seoTitolo ? _self.seoTitolo : seoTitolo // ignore: cast_nullable_to_non_nullable
as String?,seoDescrizione: null == seoDescrizione ? _self.seoDescrizione : seoDescrizione // ignore: cast_nullable_to_non_nullable
as String,faq: null == faq ? _self._faq : faq // ignore: cast_nullable_to_non_nullable
as List<DomandaFaq>,commentiAperti: null == commentiAperti ? _self.commentiAperti : commentiAperti // ignore: cast_nullable_to_non_nullable
as bool,briciole: null == briciole ? _self._briciole : briciole // ignore: cast_nullable_to_non_nullable
as List<Voce>,collegamenti: null == collegamenti ? _self.collegamenti : collegamenti // ignore: cast_nullable_to_non_nullable
as Collegamenti,correlati: null == correlati ? _self._correlati : correlati // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,precedente: freezed == precedente ? _self.precedente : precedente // ignore: cast_nullable_to_non_nullable
as ArticoloBreve?,successivo: freezed == successivo ? _self.successivo : successivo // ignore: cast_nullable_to_non_nullable
as ArticoloBreve?,gemellaLingua: freezed == gemellaLingua ? _self.gemellaLingua : gemellaLingua // ignore: cast_nullable_to_non_nullable
as Gemella?,soggetto: freezed == soggetto ? _self.soggetto : soggetto // ignore: cast_nullable_to_non_nullable
as SoggettoArticolo?,
  ));
}

/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineArticoloCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineArticoloCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$VoceCopyWith<$Res>? get sezione {
    if (_self.sezione == null) {
    return null;
  }

  return $VoceCopyWith<$Res>(_self.sezione!, (value) {
    return _then(_self.copyWith(sezione: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$AutoreBlogCopyWith<$Res>? get autore {
    if (_self.autore == null) {
    return null;
  }

  return $AutoreBlogCopyWith<$Res>(_self.autore!, (value) {
    return _then(_self.copyWith(autore: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CollegamentiCopyWith<$Res> get collegamenti {
  
  return $CollegamentiCopyWith<$Res>(_self.collegamenti, (value) {
    return _then(_self.copyWith(collegamenti: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ArticoloBreveCopyWith<$Res>? get precedente {
    if (_self.precedente == null) {
    return null;
  }

  return $ArticoloBreveCopyWith<$Res>(_self.precedente!, (value) {
    return _then(_self.copyWith(precedente: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ArticoloBreveCopyWith<$Res>? get successivo {
    if (_self.successivo == null) {
    return null;
  }

  return $ArticoloBreveCopyWith<$Res>(_self.successivo!, (value) {
    return _then(_self.copyWith(successivo: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GemellaCopyWith<$Res>? get gemellaLingua {
    if (_self.gemellaLingua == null) {
    return null;
  }

  return $GemellaCopyWith<$Res>(_self.gemellaLingua!, (value) {
    return _then(_self.copyWith(gemellaLingua: value));
  });
}/// Create a copy of ArticoloBlog
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SoggettoArticoloCopyWith<$Res>? get soggetto {
    if (_self.soggetto == null) {
    return null;
  }

  return $SoggettoArticoloCopyWith<$Res>(_self.soggetto!, (value) {
    return _then(_self.copyWith(soggetto: value));
  });
}
}


/// @nodoc
mixin _$ImmagineBlog {

 String? get url; String? get mini; String? get alt;
/// Create a copy of ImmagineBlog
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ImmagineBlogCopyWith<ImmagineBlog> get copyWith => _$ImmagineBlogCopyWithImpl<ImmagineBlog>(this as ImmagineBlog, _$identity);

  /// Serializes this ImmagineBlog to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ImmagineBlog;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ImmagineBlog&&(identical(other.url, _this.url) || other.url == _this.url)&&(identical(other.mini, _this.mini) || other.mini == _this.mini)&&(identical(other.alt, _this.alt) || other.alt == _this.alt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ImmagineBlog;
  return Object.hash(runtimeType,_this.url,_this.mini,_this.alt);
}

@override
String toString() {
  final _this = this as ImmagineBlog;
  return 'ImmagineBlog(url: ${_this.url}, mini: ${_this.mini}, alt: ${_this.alt})';
}


}

/// @nodoc
abstract mixin class $ImmagineBlogCopyWith<$Res>  {
  factory $ImmagineBlogCopyWith(ImmagineBlog value, $Res Function(ImmagineBlog) _then) = _$ImmagineBlogCopyWithImpl;
@useResult
$Res call({
 String? url, String? mini, String? alt
});




}
/// @nodoc
class _$ImmagineBlogCopyWithImpl<$Res>
    implements $ImmagineBlogCopyWith<$Res> {
  _$ImmagineBlogCopyWithImpl(this._self, this._then);

  final ImmagineBlog _self;
  final $Res Function(ImmagineBlog) _then;

/// Create a copy of ImmagineBlog
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? url = freezed,Object? mini = freezed,Object? alt = freezed,}) {
  return _then(ImmagineBlog(
url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,mini: freezed == mini ? _self.mini : mini // ignore: cast_nullable_to_non_nullable
as String?,alt: freezed == alt ? _self.alt : alt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ImmagineBlog].
extension ImmagineBlogPatterns on ImmagineBlog {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ImmagineBlog value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ImmagineBlog() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ImmagineBlog value)  $default,){
final _that = this;
switch (_that) {
case _ImmagineBlog():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ImmagineBlog value)?  $default,){
final _that = this;
switch (_that) {
case _ImmagineBlog() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? url,  String? mini,  String? alt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ImmagineBlog() when $default != null:
return $default(_that.url,_that.mini,_that.alt);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? url,  String? mini,  String? alt)  $default,) {final _that = this;
switch (_that) {
case _ImmagineBlog():
return $default(_that.url,_that.mini,_that.alt);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? url,  String? mini,  String? alt)?  $default,) {final _that = this;
switch (_that) {
case _ImmagineBlog() when $default != null:
return $default(_that.url,_that.mini,_that.alt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ImmagineBlog extends ImmagineBlog {
  const _ImmagineBlog({this.url, this.mini, this.alt}): super._();
  factory _ImmagineBlog.fromJson(Map<String, dynamic> json) => _$ImmagineBlogFromJson(json);

@override final  String? url;
@override final  String? mini;
@override final  String? alt;

/// Create a copy of ImmagineBlog
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ImmagineBlogCopyWith<_ImmagineBlog> get copyWith => __$ImmagineBlogCopyWithImpl<_ImmagineBlog>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ImmagineBlogToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ImmagineBlog&&(identical(other.url, url) || other.url == url)&&(identical(other.mini, mini) || other.mini == mini)&&(identical(other.alt, alt) || other.alt == alt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,url,mini,alt);
}

@override
String toString() {
    return 'ImmagineBlog(url: $url, mini: $mini, alt: $alt)';
}


}

/// @nodoc
abstract mixin class _$ImmagineBlogCopyWith<$Res> implements $ImmagineBlogCopyWith<$Res> {
  factory _$ImmagineBlogCopyWith(_ImmagineBlog value, $Res Function(_ImmagineBlog) _then) = __$ImmagineBlogCopyWithImpl;
@override @useResult
$Res call({
 String? url, String? mini, String? alt
});




}
/// @nodoc
class __$ImmagineBlogCopyWithImpl<$Res>
    implements _$ImmagineBlogCopyWith<$Res> {
  __$ImmagineBlogCopyWithImpl(this._self, this._then);

  final _ImmagineBlog _self;
  final $Res Function(_ImmagineBlog) _then;

/// Create a copy of ImmagineBlog
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? url = freezed,Object? mini = freezed,Object? alt = freezed,}) {
  return _then(_ImmagineBlog(
url: freezed == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String?,mini: freezed == mini ? _self.mini : mini // ignore: cast_nullable_to_non_nullable
as String?,alt: freezed == alt ? _self.alt : alt // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$NodoSezione {

 int get id; String get slug; String get nome; String? get descrizione;/// `articoli`, `carte`, `stese`, `contenitore`.
 String get tipo; Map<String, String>? get filtro;@ImmagineBlogJson() ImmagineBlog? get immagine;/// Gli articoli di tutto il ramo (la sezione e le sotto-sezioni).
 int get nArticoli;/// Solo quelli della sezione.
 int? get nArticoliDiretti; int? get nElementi;/// Le carte e le stese diverse di tutto il ramo.
 int get nCarte; int get nStese; List<NodoSezione> get figli;/// Solo nei figli di `GET /blog/sections/{slug}` (v9.4): 3 articoli del ramo scelti per la giornata.
 List<ArticoloBreve> get articoli;
/// Create a copy of NodoSezione
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NodoSezioneCopyWith<NodoSezione> get copyWith => _$NodoSezioneCopyWithImpl<NodoSezione>(this as NodoSezione, _$identity);

  /// Serializes this NodoSezione to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as NodoSezione;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NodoSezione&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.descrizione, _this.descrizione) || other.descrizione == _this.descrizione)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&const DeepCollectionEquality().equals(other.filtro, _this.filtro)&&(identical(other.immagine, _this.immagine) || other.immagine == _this.immagine)&&(identical(other.nArticoli, _this.nArticoli) || other.nArticoli == _this.nArticoli)&&(identical(other.nArticoliDiretti, _this.nArticoliDiretti) || other.nArticoliDiretti == _this.nArticoliDiretti)&&(identical(other.nElementi, _this.nElementi) || other.nElementi == _this.nElementi)&&(identical(other.nCarte, _this.nCarte) || other.nCarte == _this.nCarte)&&(identical(other.nStese, _this.nStese) || other.nStese == _this.nStese)&&const DeepCollectionEquality().equals(other.figli, _this.figli)&&const DeepCollectionEquality().equals(other.articoli, _this.articoli));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as NodoSezione;
  return Object.hash(runtimeType,_this.id,_this.slug,_this.nome,_this.descrizione,_this.tipo,const DeepCollectionEquality().hash(_this.filtro),_this.immagine,_this.nArticoli,_this.nArticoliDiretti,_this.nElementi,_this.nCarte,_this.nStese,const DeepCollectionEquality().hash(_this.figli),const DeepCollectionEquality().hash(_this.articoli));
}

@override
String toString() {
  final _this = this as NodoSezione;
  return 'NodoSezione(id: ${_this.id}, slug: ${_this.slug}, nome: ${_this.nome}, descrizione: ${_this.descrizione}, tipo: ${_this.tipo}, filtro: ${_this.filtro}, immagine: ${_this.immagine}, nArticoli: ${_this.nArticoli}, nArticoliDiretti: ${_this.nArticoliDiretti}, nElementi: ${_this.nElementi}, nCarte: ${_this.nCarte}, nStese: ${_this.nStese}, figli: ${_this.figli}, articoli: ${_this.articoli})';
}


}

/// @nodoc
abstract mixin class $NodoSezioneCopyWith<$Res>  {
  factory $NodoSezioneCopyWith(NodoSezione value, $Res Function(NodoSezione) _then) = _$NodoSezioneCopyWithImpl;
@useResult
$Res call({
 int id, String slug, String nome, String? descrizione, String tipo, Map<String, String>? filtro,@ImmagineBlogJson() ImmagineBlog? immagine, int nArticoli, int? nArticoliDiretti, int? nElementi, int nCarte, int nStese, List<NodoSezione> figli, List<ArticoloBreve> articoli
});


$ImmagineBlogCopyWith<$Res>? get immagine;

}
/// @nodoc
class _$NodoSezioneCopyWithImpl<$Res>
    implements $NodoSezioneCopyWith<$Res> {
  _$NodoSezioneCopyWithImpl(this._self, this._then);

  final NodoSezione _self;
  final $Res Function(NodoSezione) _then;

/// Create a copy of NodoSezione
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? nome = null,Object? descrizione = freezed,Object? tipo = null,Object? filtro = freezed,Object? immagine = freezed,Object? nArticoli = null,Object? nArticoliDiretti = freezed,Object? nElementi = freezed,Object? nCarte = null,Object? nStese = null,Object? figli = null,Object? articoli = null,}) {
  return _then(NodoSezione(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,filtro: freezed == filtro ? _self.filtro : filtro // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineBlog?,nArticoli: null == nArticoli ? _self.nArticoli : nArticoli // ignore: cast_nullable_to_non_nullable
as int,nArticoliDiretti: freezed == nArticoliDiretti ? _self.nArticoliDiretti : nArticoliDiretti // ignore: cast_nullable_to_non_nullable
as int?,nElementi: freezed == nElementi ? _self.nElementi : nElementi // ignore: cast_nullable_to_non_nullable
as int?,nCarte: null == nCarte ? _self.nCarte : nCarte // ignore: cast_nullable_to_non_nullable
as int,nStese: null == nStese ? _self.nStese : nStese // ignore: cast_nullable_to_non_nullable
as int,figli: null == figli ? _self.figli : figli // ignore: cast_nullable_to_non_nullable
as List<NodoSezione>,articoli: null == articoli ? _self.articoli : articoli // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,
  ));
}
/// Create a copy of NodoSezione
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineBlogCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineBlogCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}
}


/// Adds pattern-matching-related methods to [NodoSezione].
extension NodoSezionePatterns on NodoSezione {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _NodoSezione value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _NodoSezione() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _NodoSezione value)  $default,){
final _that = this;
switch (_that) {
case _NodoSezione():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _NodoSezione value)?  $default,){
final _that = this;
switch (_that) {
case _NodoSezione() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String slug,  String nome,  String? descrizione,  String tipo,  Map<String, String>? filtro, @ImmagineBlogJson()  ImmagineBlog? immagine,  int nArticoli,  int? nArticoliDiretti,  int? nElementi,  int nCarte,  int nStese,  List<NodoSezione> figli,  List<ArticoloBreve> articoli)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _NodoSezione() when $default != null:
return $default(_that.id,_that.slug,_that.nome,_that.descrizione,_that.tipo,_that.filtro,_that.immagine,_that.nArticoli,_that.nArticoliDiretti,_that.nElementi,_that.nCarte,_that.nStese,_that.figli,_that.articoli);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String slug,  String nome,  String? descrizione,  String tipo,  Map<String, String>? filtro, @ImmagineBlogJson()  ImmagineBlog? immagine,  int nArticoli,  int? nArticoliDiretti,  int? nElementi,  int nCarte,  int nStese,  List<NodoSezione> figli,  List<ArticoloBreve> articoli)  $default,) {final _that = this;
switch (_that) {
case _NodoSezione():
return $default(_that.id,_that.slug,_that.nome,_that.descrizione,_that.tipo,_that.filtro,_that.immagine,_that.nArticoli,_that.nArticoliDiretti,_that.nElementi,_that.nCarte,_that.nStese,_that.figli,_that.articoli);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String slug,  String nome,  String? descrizione,  String tipo,  Map<String, String>? filtro, @ImmagineBlogJson()  ImmagineBlog? immagine,  int nArticoli,  int? nArticoliDiretti,  int? nElementi,  int nCarte,  int nStese,  List<NodoSezione> figli,  List<ArticoloBreve> articoli)?  $default,) {final _that = this;
switch (_that) {
case _NodoSezione() when $default != null:
return $default(_that.id,_that.slug,_that.nome,_that.descrizione,_that.tipo,_that.filtro,_that.immagine,_that.nArticoli,_that.nArticoliDiretti,_that.nElementi,_that.nCarte,_that.nStese,_that.figli,_that.articoli);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _NodoSezione implements NodoSezione {
  const _NodoSezione({required this.id, required this.slug, required this.nome, this.descrizione, this.tipo = 'articoli',  Map<String, String>? filtro, @ImmagineBlogJson() this.immagine, this.nArticoli = 0, this.nArticoliDiretti, this.nElementi, this.nCarte = 0, this.nStese = 0,  List<NodoSezione> figli = const <NodoSezione>[],  List<ArticoloBreve> articoli = const <ArticoloBreve>[]}): _filtro = filtro,_figli = figli,_articoli = articoli;
  factory _NodoSezione.fromJson(Map<String, dynamic> json) => _$NodoSezioneFromJson(json);

@override final  int id;
@override final  String slug;
@override final  String nome;
@override final  String? descrizione;
/// `articoli`, `carte`, `stese`, `contenitore`.
@override@JsonKey() final  String tipo;
 final  Map<String, String>? _filtro;
@override Map<String, String>? get filtro {
  final value = _filtro;
  if (value == null) return null;
  if (_filtro is EqualUnmodifiableMapView) return _filtro;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@ImmagineBlogJson() final  ImmagineBlog? immagine;
/// Gli articoli di tutto il ramo (la sezione e le sotto-sezioni).
@override@JsonKey() final  int nArticoli;
/// Solo quelli della sezione.
@override final  int? nArticoliDiretti;
@override final  int? nElementi;
/// Le carte e le stese diverse di tutto il ramo.
@override@JsonKey() final  int nCarte;
@override@JsonKey() final  int nStese;
 final  List<NodoSezione> _figli;
@override@JsonKey() List<NodoSezione> get figli {
  if (_figli is EqualUnmodifiableListView) return _figli;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_figli);
}

/// Solo nei figli di `GET /blog/sections/{slug}` (v9.4): 3 articoli del ramo scelti per la giornata.
 final  List<ArticoloBreve> _articoli;
/// Solo nei figli di `GET /blog/sections/{slug}` (v9.4): 3 articoli del ramo scelti per la giornata.
@override@JsonKey() List<ArticoloBreve> get articoli {
  if (_articoli is EqualUnmodifiableListView) return _articoli;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_articoli);
}


/// Create a copy of NodoSezione
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$NodoSezioneCopyWith<_NodoSezione> get copyWith => __$NodoSezioneCopyWithImpl<_NodoSezione>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$NodoSezioneToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _NodoSezione&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.descrizione, descrizione) || other.descrizione == descrizione)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&const DeepCollectionEquality().equals(other.filtro, _filtro)&&(identical(other.immagine, immagine) || other.immagine == immagine)&&(identical(other.nArticoli, nArticoli) || other.nArticoli == nArticoli)&&(identical(other.nArticoliDiretti, nArticoliDiretti) || other.nArticoliDiretti == nArticoliDiretti)&&(identical(other.nElementi, nElementi) || other.nElementi == nElementi)&&(identical(other.nCarte, nCarte) || other.nCarte == nCarte)&&(identical(other.nStese, nStese) || other.nStese == nStese)&&const DeepCollectionEquality().equals(other.figli, _figli)&&const DeepCollectionEquality().equals(other.articoli, _articoli));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,slug,nome,descrizione,tipo,const DeepCollectionEquality().hash(_filtro),immagine,nArticoli,nArticoliDiretti,nElementi,nCarte,nStese,const DeepCollectionEquality().hash(_figli),const DeepCollectionEquality().hash(_articoli));
}

@override
String toString() {
    return 'NodoSezione(id: $id, slug: $slug, nome: $nome, descrizione: $descrizione, tipo: $tipo, filtro: $filtro, immagine: $immagine, nArticoli: $nArticoli, nArticoliDiretti: $nArticoliDiretti, nElementi: $nElementi, nCarte: $nCarte, nStese: $nStese, figli: $figli, articoli: $articoli)';
}


}

/// @nodoc
abstract mixin class _$NodoSezioneCopyWith<$Res> implements $NodoSezioneCopyWith<$Res> {
  factory _$NodoSezioneCopyWith(_NodoSezione value, $Res Function(_NodoSezione) _then) = __$NodoSezioneCopyWithImpl;
@override @useResult
$Res call({
 int id, String slug, String nome, String? descrizione, String tipo, Map<String, String>? filtro,@ImmagineBlogJson() ImmagineBlog? immagine, int nArticoli, int? nArticoliDiretti, int? nElementi, int nCarte, int nStese, List<NodoSezione> figli, List<ArticoloBreve> articoli
});


@override $ImmagineBlogCopyWith<$Res>? get immagine;

}
/// @nodoc
class __$NodoSezioneCopyWithImpl<$Res>
    implements _$NodoSezioneCopyWith<$Res> {
  __$NodoSezioneCopyWithImpl(this._self, this._then);

  final _NodoSezione _self;
  final $Res Function(_NodoSezione) _then;

/// Create a copy of NodoSezione
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? nome = null,Object? descrizione = freezed,Object? tipo = null,Object? filtro = freezed,Object? immagine = freezed,Object? nArticoli = null,Object? nArticoliDiretti = freezed,Object? nElementi = freezed,Object? nCarte = null,Object? nStese = null,Object? figli = null,Object? articoli = null,}) {
  return _then(_NodoSezione(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,filtro: freezed == filtro ? _self._filtro : filtro // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineBlog?,nArticoli: null == nArticoli ? _self.nArticoli : nArticoli // ignore: cast_nullable_to_non_nullable
as int,nArticoliDiretti: freezed == nArticoliDiretti ? _self.nArticoliDiretti : nArticoliDiretti // ignore: cast_nullable_to_non_nullable
as int?,nElementi: freezed == nElementi ? _self.nElementi : nElementi // ignore: cast_nullable_to_non_nullable
as int?,nCarte: null == nCarte ? _self.nCarte : nCarte // ignore: cast_nullable_to_non_nullable
as int,nStese: null == nStese ? _self.nStese : nStese // ignore: cast_nullable_to_non_nullable
as int,figli: null == figli ? _self._figli : figli // ignore: cast_nullable_to_non_nullable
as List<NodoSezione>,articoli: null == articoli ? _self._articoli : articoli // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,
  ));
}

/// Create a copy of NodoSezione
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineBlogCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineBlogCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}
}


/// @nodoc
mixin _$DettaglioSezione {

 int get id; String get slug; String get nome; String? get descrizione; String get tipo; Map<String, String>? get filtro;@ImmagineBlogJson() ImmagineBlog? get immagine; int get nArticoli; int? get nArticoliDiretti; int? get nElementi; int get nCarte; int get nStese;/// Le sotto-sezioni dirette, ognuna coi suoi 3 `articoli` (v9.4).
 List<NodoSezione> get figli; String? get seoTitolo; String? get seoDescrizione; List<Voce> get briciole;/// Le carte (sezioni `carte`: la forma di `GET /cards`) o le stese (sezioni `stese`: vedi [StesaSezione]).
 List<Map<String, Object?>> get elementi;
/// Create a copy of DettaglioSezione
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DettaglioSezioneCopyWith<DettaglioSezione> get copyWith => _$DettaglioSezioneCopyWithImpl<DettaglioSezione>(this as DettaglioSezione, _$identity);

  /// Serializes this DettaglioSezione to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as DettaglioSezione;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DettaglioSezione&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.descrizione, _this.descrizione) || other.descrizione == _this.descrizione)&&(identical(other.tipo, _this.tipo) || other.tipo == _this.tipo)&&const DeepCollectionEquality().equals(other.filtro, _this.filtro)&&(identical(other.immagine, _this.immagine) || other.immagine == _this.immagine)&&(identical(other.nArticoli, _this.nArticoli) || other.nArticoli == _this.nArticoli)&&(identical(other.nArticoliDiretti, _this.nArticoliDiretti) || other.nArticoliDiretti == _this.nArticoliDiretti)&&(identical(other.nElementi, _this.nElementi) || other.nElementi == _this.nElementi)&&(identical(other.nCarte, _this.nCarte) || other.nCarte == _this.nCarte)&&(identical(other.nStese, _this.nStese) || other.nStese == _this.nStese)&&const DeepCollectionEquality().equals(other.figli, _this.figli)&&(identical(other.seoTitolo, _this.seoTitolo) || other.seoTitolo == _this.seoTitolo)&&(identical(other.seoDescrizione, _this.seoDescrizione) || other.seoDescrizione == _this.seoDescrizione)&&const DeepCollectionEquality().equals(other.briciole, _this.briciole)&&const DeepCollectionEquality().equals(other.elementi, _this.elementi));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as DettaglioSezione;
  return Object.hash(runtimeType,_this.id,_this.slug,_this.nome,_this.descrizione,_this.tipo,const DeepCollectionEquality().hash(_this.filtro),_this.immagine,_this.nArticoli,_this.nArticoliDiretti,_this.nElementi,_this.nCarte,_this.nStese,const DeepCollectionEquality().hash(_this.figli),_this.seoTitolo,_this.seoDescrizione,const DeepCollectionEquality().hash(_this.briciole),const DeepCollectionEquality().hash(_this.elementi));
}

@override
String toString() {
  final _this = this as DettaglioSezione;
  return 'DettaglioSezione(id: ${_this.id}, slug: ${_this.slug}, nome: ${_this.nome}, descrizione: ${_this.descrizione}, tipo: ${_this.tipo}, filtro: ${_this.filtro}, immagine: ${_this.immagine}, nArticoli: ${_this.nArticoli}, nArticoliDiretti: ${_this.nArticoliDiretti}, nElementi: ${_this.nElementi}, nCarte: ${_this.nCarte}, nStese: ${_this.nStese}, figli: ${_this.figli}, seoTitolo: ${_this.seoTitolo}, seoDescrizione: ${_this.seoDescrizione}, briciole: ${_this.briciole}, elementi: ${_this.elementi})';
}


}

/// @nodoc
abstract mixin class $DettaglioSezioneCopyWith<$Res>  {
  factory $DettaglioSezioneCopyWith(DettaglioSezione value, $Res Function(DettaglioSezione) _then) = _$DettaglioSezioneCopyWithImpl;
@useResult
$Res call({
 int id, String slug, String nome, String? descrizione, String tipo, Map<String, String>? filtro,@ImmagineBlogJson() ImmagineBlog? immagine, int nArticoli, int? nArticoliDiretti, int? nElementi, int nCarte, int nStese, List<NodoSezione> figli, String? seoTitolo, String? seoDescrizione, List<Voce> briciole, List<Map<String, Object?>> elementi
});


$ImmagineBlogCopyWith<$Res>? get immagine;

}
/// @nodoc
class _$DettaglioSezioneCopyWithImpl<$Res>
    implements $DettaglioSezioneCopyWith<$Res> {
  _$DettaglioSezioneCopyWithImpl(this._self, this._then);

  final DettaglioSezione _self;
  final $Res Function(DettaglioSezione) _then;

/// Create a copy of DettaglioSezione
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? nome = null,Object? descrizione = freezed,Object? tipo = null,Object? filtro = freezed,Object? immagine = freezed,Object? nArticoli = null,Object? nArticoliDiretti = freezed,Object? nElementi = freezed,Object? nCarte = null,Object? nStese = null,Object? figli = null,Object? seoTitolo = freezed,Object? seoDescrizione = freezed,Object? briciole = null,Object? elementi = null,}) {
  return _then(DettaglioSezione(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,filtro: freezed == filtro ? _self.filtro : filtro // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineBlog?,nArticoli: null == nArticoli ? _self.nArticoli : nArticoli // ignore: cast_nullable_to_non_nullable
as int,nArticoliDiretti: freezed == nArticoliDiretti ? _self.nArticoliDiretti : nArticoliDiretti // ignore: cast_nullable_to_non_nullable
as int?,nElementi: freezed == nElementi ? _self.nElementi : nElementi // ignore: cast_nullable_to_non_nullable
as int?,nCarte: null == nCarte ? _self.nCarte : nCarte // ignore: cast_nullable_to_non_nullable
as int,nStese: null == nStese ? _self.nStese : nStese // ignore: cast_nullable_to_non_nullable
as int,figli: null == figli ? _self.figli : figli // ignore: cast_nullable_to_non_nullable
as List<NodoSezione>,seoTitolo: freezed == seoTitolo ? _self.seoTitolo : seoTitolo // ignore: cast_nullable_to_non_nullable
as String?,seoDescrizione: freezed == seoDescrizione ? _self.seoDescrizione : seoDescrizione // ignore: cast_nullable_to_non_nullable
as String?,briciole: null == briciole ? _self.briciole : briciole // ignore: cast_nullable_to_non_nullable
as List<Voce>,elementi: null == elementi ? _self.elementi : elementi // ignore: cast_nullable_to_non_nullable
as List<Map<String, Object?>>,
  ));
}
/// Create a copy of DettaglioSezione
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineBlogCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineBlogCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}
}


/// Adds pattern-matching-related methods to [DettaglioSezione].
extension DettaglioSezionePatterns on DettaglioSezione {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DettaglioSezione value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DettaglioSezione() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DettaglioSezione value)  $default,){
final _that = this;
switch (_that) {
case _DettaglioSezione():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DettaglioSezione value)?  $default,){
final _that = this;
switch (_that) {
case _DettaglioSezione() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String slug,  String nome,  String? descrizione,  String tipo,  Map<String, String>? filtro, @ImmagineBlogJson()  ImmagineBlog? immagine,  int nArticoli,  int? nArticoliDiretti,  int? nElementi,  int nCarte,  int nStese,  List<NodoSezione> figli,  String? seoTitolo,  String? seoDescrizione,  List<Voce> briciole,  List<Map<String, Object?>> elementi)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DettaglioSezione() when $default != null:
return $default(_that.id,_that.slug,_that.nome,_that.descrizione,_that.tipo,_that.filtro,_that.immagine,_that.nArticoli,_that.nArticoliDiretti,_that.nElementi,_that.nCarte,_that.nStese,_that.figli,_that.seoTitolo,_that.seoDescrizione,_that.briciole,_that.elementi);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String slug,  String nome,  String? descrizione,  String tipo,  Map<String, String>? filtro, @ImmagineBlogJson()  ImmagineBlog? immagine,  int nArticoli,  int? nArticoliDiretti,  int? nElementi,  int nCarte,  int nStese,  List<NodoSezione> figli,  String? seoTitolo,  String? seoDescrizione,  List<Voce> briciole,  List<Map<String, Object?>> elementi)  $default,) {final _that = this;
switch (_that) {
case _DettaglioSezione():
return $default(_that.id,_that.slug,_that.nome,_that.descrizione,_that.tipo,_that.filtro,_that.immagine,_that.nArticoli,_that.nArticoliDiretti,_that.nElementi,_that.nCarte,_that.nStese,_that.figli,_that.seoTitolo,_that.seoDescrizione,_that.briciole,_that.elementi);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String slug,  String nome,  String? descrizione,  String tipo,  Map<String, String>? filtro, @ImmagineBlogJson()  ImmagineBlog? immagine,  int nArticoli,  int? nArticoliDiretti,  int? nElementi,  int nCarte,  int nStese,  List<NodoSezione> figli,  String? seoTitolo,  String? seoDescrizione,  List<Voce> briciole,  List<Map<String, Object?>> elementi)?  $default,) {final _that = this;
switch (_that) {
case _DettaglioSezione() when $default != null:
return $default(_that.id,_that.slug,_that.nome,_that.descrizione,_that.tipo,_that.filtro,_that.immagine,_that.nArticoli,_that.nArticoliDiretti,_that.nElementi,_that.nCarte,_that.nStese,_that.figli,_that.seoTitolo,_that.seoDescrizione,_that.briciole,_that.elementi);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _DettaglioSezione extends DettaglioSezione {
  const _DettaglioSezione({required this.id, required this.slug, required this.nome, this.descrizione, this.tipo = 'articoli',  Map<String, String>? filtro, @ImmagineBlogJson() this.immagine, this.nArticoli = 0, this.nArticoliDiretti, this.nElementi, this.nCarte = 0, this.nStese = 0,  List<NodoSezione> figli = const <NodoSezione>[], this.seoTitolo, this.seoDescrizione,  List<Voce> briciole = const <Voce>[],  List<Map<String, Object?>> elementi = const <Map<String, Object?>>[]}): _filtro = filtro,_figli = figli,_briciole = briciole,_elementi = elementi,super._();
  factory _DettaglioSezione.fromJson(Map<String, dynamic> json) => _$DettaglioSezioneFromJson(json);

@override final  int id;
@override final  String slug;
@override final  String nome;
@override final  String? descrizione;
@override@JsonKey() final  String tipo;
 final  Map<String, String>? _filtro;
@override Map<String, String>? get filtro {
  final value = _filtro;
  if (value == null) return null;
  if (_filtro is EqualUnmodifiableMapView) return _filtro;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@ImmagineBlogJson() final  ImmagineBlog? immagine;
@override@JsonKey() final  int nArticoli;
@override final  int? nArticoliDiretti;
@override final  int? nElementi;
@override@JsonKey() final  int nCarte;
@override@JsonKey() final  int nStese;
/// Le sotto-sezioni dirette, ognuna coi suoi 3 `articoli` (v9.4).
 final  List<NodoSezione> _figli;
/// Le sotto-sezioni dirette, ognuna coi suoi 3 `articoli` (v9.4).
@override@JsonKey() List<NodoSezione> get figli {
  if (_figli is EqualUnmodifiableListView) return _figli;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_figli);
}

@override final  String? seoTitolo;
@override final  String? seoDescrizione;
 final  List<Voce> _briciole;
@override@JsonKey() List<Voce> get briciole {
  if (_briciole is EqualUnmodifiableListView) return _briciole;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_briciole);
}

/// Le carte (sezioni `carte`: la forma di `GET /cards`) o le stese (sezioni `stese`: vedi [StesaSezione]).
 final  List<Map<String, Object?>> _elementi;
/// Le carte (sezioni `carte`: la forma di `GET /cards`) o le stese (sezioni `stese`: vedi [StesaSezione]).
@override@JsonKey() List<Map<String, Object?>> get elementi {
  if (_elementi is EqualUnmodifiableListView) return _elementi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_elementi);
}


/// Create a copy of DettaglioSezione
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DettaglioSezioneCopyWith<_DettaglioSezione> get copyWith => __$DettaglioSezioneCopyWithImpl<_DettaglioSezione>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DettaglioSezioneToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _DettaglioSezione&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.descrizione, descrizione) || other.descrizione == descrizione)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&const DeepCollectionEquality().equals(other.filtro, _filtro)&&(identical(other.immagine, immagine) || other.immagine == immagine)&&(identical(other.nArticoli, nArticoli) || other.nArticoli == nArticoli)&&(identical(other.nArticoliDiretti, nArticoliDiretti) || other.nArticoliDiretti == nArticoliDiretti)&&(identical(other.nElementi, nElementi) || other.nElementi == nElementi)&&(identical(other.nCarte, nCarte) || other.nCarte == nCarte)&&(identical(other.nStese, nStese) || other.nStese == nStese)&&const DeepCollectionEquality().equals(other.figli, _figli)&&(identical(other.seoTitolo, seoTitolo) || other.seoTitolo == seoTitolo)&&(identical(other.seoDescrizione, seoDescrizione) || other.seoDescrizione == seoDescrizione)&&const DeepCollectionEquality().equals(other.briciole, _briciole)&&const DeepCollectionEquality().equals(other.elementi, _elementi));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,slug,nome,descrizione,tipo,const DeepCollectionEquality().hash(_filtro),immagine,nArticoli,nArticoliDiretti,nElementi,nCarte,nStese,const DeepCollectionEquality().hash(_figli),seoTitolo,seoDescrizione,const DeepCollectionEquality().hash(_briciole),const DeepCollectionEquality().hash(_elementi));
}

@override
String toString() {
    return 'DettaglioSezione(id: $id, slug: $slug, nome: $nome, descrizione: $descrizione, tipo: $tipo, filtro: $filtro, immagine: $immagine, nArticoli: $nArticoli, nArticoliDiretti: $nArticoliDiretti, nElementi: $nElementi, nCarte: $nCarte, nStese: $nStese, figli: $figli, seoTitolo: $seoTitolo, seoDescrizione: $seoDescrizione, briciole: $briciole, elementi: $elementi)';
}


}

/// @nodoc
abstract mixin class _$DettaglioSezioneCopyWith<$Res> implements $DettaglioSezioneCopyWith<$Res> {
  factory _$DettaglioSezioneCopyWith(_DettaglioSezione value, $Res Function(_DettaglioSezione) _then) = __$DettaglioSezioneCopyWithImpl;
@override @useResult
$Res call({
 int id, String slug, String nome, String? descrizione, String tipo, Map<String, String>? filtro,@ImmagineBlogJson() ImmagineBlog? immagine, int nArticoli, int? nArticoliDiretti, int? nElementi, int nCarte, int nStese, List<NodoSezione> figli, String? seoTitolo, String? seoDescrizione, List<Voce> briciole, List<Map<String, Object?>> elementi
});


@override $ImmagineBlogCopyWith<$Res>? get immagine;

}
/// @nodoc
class __$DettaglioSezioneCopyWithImpl<$Res>
    implements _$DettaglioSezioneCopyWith<$Res> {
  __$DettaglioSezioneCopyWithImpl(this._self, this._then);

  final _DettaglioSezione _self;
  final $Res Function(_DettaglioSezione) _then;

/// Create a copy of DettaglioSezione
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? nome = null,Object? descrizione = freezed,Object? tipo = null,Object? filtro = freezed,Object? immagine = freezed,Object? nArticoli = null,Object? nArticoliDiretti = freezed,Object? nElementi = freezed,Object? nCarte = null,Object? nStese = null,Object? figli = null,Object? seoTitolo = freezed,Object? seoDescrizione = freezed,Object? briciole = null,Object? elementi = null,}) {
  return _then(_DettaglioSezione(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,descrizione: freezed == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String?,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as String,filtro: freezed == filtro ? _self._filtro : filtro // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineBlog?,nArticoli: null == nArticoli ? _self.nArticoli : nArticoli // ignore: cast_nullable_to_non_nullable
as int,nArticoliDiretti: freezed == nArticoliDiretti ? _self.nArticoliDiretti : nArticoliDiretti // ignore: cast_nullable_to_non_nullable
as int?,nElementi: freezed == nElementi ? _self.nElementi : nElementi // ignore: cast_nullable_to_non_nullable
as int?,nCarte: null == nCarte ? _self.nCarte : nCarte // ignore: cast_nullable_to_non_nullable
as int,nStese: null == nStese ? _self.nStese : nStese // ignore: cast_nullable_to_non_nullable
as int,figli: null == figli ? _self._figli : figli // ignore: cast_nullable_to_non_nullable
as List<NodoSezione>,seoTitolo: freezed == seoTitolo ? _self.seoTitolo : seoTitolo // ignore: cast_nullable_to_non_nullable
as String?,seoDescrizione: freezed == seoDescrizione ? _self.seoDescrizione : seoDescrizione // ignore: cast_nullable_to_non_nullable
as String?,briciole: null == briciole ? _self._briciole : briciole // ignore: cast_nullable_to_non_nullable
as List<Voce>,elementi: null == elementi ? _self._elementi : elementi // ignore: cast_nullable_to_non_nullable
as List<Map<String, Object?>>,
  ));
}

/// Create a copy of DettaglioSezione
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineBlogCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineBlogCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}
}


/// @nodoc
mixin _$StesaSezione {

 String get id; String get nome; Map<String, String>? get nomi; String get descrizione;/// La descrizione accorciata (al più 160 caratteri).
 String get descrizioneBreve; String get categoria; String? get stile; List<Posizione> get posizioni; String? get lang; String? get slug; Map<String, String>? get slugs;/// La tradizione in poche parole («love», «Celtic tradition»), nella lingua dei testi.
 String? get tradizione;/// La tradizione in ogni lingua che ce l'ha.
 Map<String, String>? get tradizioni; String get forma; double? get larghezza; double? get larghezzaStretto; int? get carteDaScegliere; String get mazzo; int? get nCarte;@ImmagineBlogJson() ImmagineBlog? get immagine;
/// Create a copy of StesaSezione
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StesaSezioneCopyWith<StesaSezione> get copyWith => _$StesaSezioneCopyWithImpl<StesaSezione>(this as StesaSezione, _$identity);

  /// Serializes this StesaSezione to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as StesaSezione;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StesaSezione&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&const DeepCollectionEquality().equals(other.nomi, _this.nomi)&&(identical(other.descrizione, _this.descrizione) || other.descrizione == _this.descrizione)&&(identical(other.descrizioneBreve, _this.descrizioneBreve) || other.descrizioneBreve == _this.descrizioneBreve)&&(identical(other.categoria, _this.categoria) || other.categoria == _this.categoria)&&(identical(other.stile, _this.stile) || other.stile == _this.stile)&&const DeepCollectionEquality().equals(other.posizioni, _this.posizioni)&&(identical(other.lang, _this.lang) || other.lang == _this.lang)&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&const DeepCollectionEquality().equals(other.slugs, _this.slugs)&&(identical(other.tradizione, _this.tradizione) || other.tradizione == _this.tradizione)&&const DeepCollectionEquality().equals(other.tradizioni, _this.tradizioni)&&(identical(other.forma, _this.forma) || other.forma == _this.forma)&&(identical(other.larghezza, _this.larghezza) || other.larghezza == _this.larghezza)&&(identical(other.larghezzaStretto, _this.larghezzaStretto) || other.larghezzaStretto == _this.larghezzaStretto)&&(identical(other.carteDaScegliere, _this.carteDaScegliere) || other.carteDaScegliere == _this.carteDaScegliere)&&(identical(other.mazzo, _this.mazzo) || other.mazzo == _this.mazzo)&&(identical(other.nCarte, _this.nCarte) || other.nCarte == _this.nCarte)&&(identical(other.immagine, _this.immagine) || other.immagine == _this.immagine));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as StesaSezione;
  return Object.hashAll([runtimeType,_this.id,_this.nome,const DeepCollectionEquality().hash(_this.nomi),_this.descrizione,_this.descrizioneBreve,_this.categoria,_this.stile,const DeepCollectionEquality().hash(_this.posizioni),_this.lang,_this.slug,const DeepCollectionEquality().hash(_this.slugs),_this.tradizione,const DeepCollectionEquality().hash(_this.tradizioni),_this.forma,_this.larghezza,_this.larghezzaStretto,_this.carteDaScegliere,_this.mazzo,_this.nCarte,_this.immagine]);
}

@override
String toString() {
  final _this = this as StesaSezione;
  return 'StesaSezione(id: ${_this.id}, nome: ${_this.nome}, nomi: ${_this.nomi}, descrizione: ${_this.descrizione}, descrizioneBreve: ${_this.descrizioneBreve}, categoria: ${_this.categoria}, stile: ${_this.stile}, posizioni: ${_this.posizioni}, lang: ${_this.lang}, slug: ${_this.slug}, slugs: ${_this.slugs}, tradizione: ${_this.tradizione}, tradizioni: ${_this.tradizioni}, forma: ${_this.forma}, larghezza: ${_this.larghezza}, larghezzaStretto: ${_this.larghezzaStretto}, carteDaScegliere: ${_this.carteDaScegliere}, mazzo: ${_this.mazzo}, nCarte: ${_this.nCarte}, immagine: ${_this.immagine})';
}


}

/// @nodoc
abstract mixin class $StesaSezioneCopyWith<$Res>  {
  factory $StesaSezioneCopyWith(StesaSezione value, $Res Function(StesaSezione) _then) = _$StesaSezioneCopyWithImpl;
@useResult
$Res call({
 String id, String nome, Map<String, String>? nomi, String descrizione, String descrizioneBreve, String categoria, String? stile, List<Posizione> posizioni, String? lang, String? slug, Map<String, String>? slugs, String? tradizione, Map<String, String>? tradizioni, String forma, double? larghezza, double? larghezzaStretto, int? carteDaScegliere, String mazzo, int? nCarte,@ImmagineBlogJson() ImmagineBlog? immagine
});


$ImmagineBlogCopyWith<$Res>? get immagine;

}
/// @nodoc
class _$StesaSezioneCopyWithImpl<$Res>
    implements $StesaSezioneCopyWith<$Res> {
  _$StesaSezioneCopyWithImpl(this._self, this._then);

  final StesaSezione _self;
  final $Res Function(StesaSezione) _then;

/// Create a copy of StesaSezione
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nome = null,Object? nomi = freezed,Object? descrizione = null,Object? descrizioneBreve = null,Object? categoria = null,Object? stile = freezed,Object? posizioni = null,Object? lang = freezed,Object? slug = freezed,Object? slugs = freezed,Object? tradizione = freezed,Object? tradizioni = freezed,Object? forma = null,Object? larghezza = freezed,Object? larghezzaStretto = freezed,Object? carteDaScegliere = freezed,Object? mazzo = null,Object? nCarte = freezed,Object? immagine = freezed,}) {
  return _then(StesaSezione(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,nomi: freezed == nomi ? _self.nomi : nomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,descrizione: null == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String,descrizioneBreve: null == descrizioneBreve ? _self.descrizioneBreve : descrizioneBreve // ignore: cast_nullable_to_non_nullable
as String,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,stile: freezed == stile ? _self.stile : stile // ignore: cast_nullable_to_non_nullable
as String?,posizioni: null == posizioni ? _self.posizioni : posizioni // ignore: cast_nullable_to_non_nullable
as List<Posizione>,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,slugs: freezed == slugs ? _self.slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,tradizione: freezed == tradizione ? _self.tradizione : tradizione // ignore: cast_nullable_to_non_nullable
as String?,tradizioni: freezed == tradizioni ? _self.tradizioni : tradizioni // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,forma: null == forma ? _self.forma : forma // ignore: cast_nullable_to_non_nullable
as String,larghezza: freezed == larghezza ? _self.larghezza : larghezza // ignore: cast_nullable_to_non_nullable
as double?,larghezzaStretto: freezed == larghezzaStretto ? _self.larghezzaStretto : larghezzaStretto // ignore: cast_nullable_to_non_nullable
as double?,carteDaScegliere: freezed == carteDaScegliere ? _self.carteDaScegliere : carteDaScegliere // ignore: cast_nullable_to_non_nullable
as int?,mazzo: null == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String,nCarte: freezed == nCarte ? _self.nCarte : nCarte // ignore: cast_nullable_to_non_nullable
as int?,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineBlog?,
  ));
}
/// Create a copy of StesaSezione
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineBlogCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineBlogCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}
}


/// Adds pattern-matching-related methods to [StesaSezione].
extension StesaSezionePatterns on StesaSezione {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StesaSezione value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StesaSezione() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StesaSezione value)  $default,){
final _that = this;
switch (_that) {
case _StesaSezione():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StesaSezione value)?  $default,){
final _that = this;
switch (_that) {
case _StesaSezione() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String nome,  Map<String, String>? nomi,  String descrizione,  String descrizioneBreve,  String categoria,  String? stile,  List<Posizione> posizioni,  String? lang,  String? slug,  Map<String, String>? slugs,  String? tradizione,  Map<String, String>? tradizioni,  String forma,  double? larghezza,  double? larghezzaStretto,  int? carteDaScegliere,  String mazzo,  int? nCarte, @ImmagineBlogJson()  ImmagineBlog? immagine)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StesaSezione() when $default != null:
return $default(_that.id,_that.nome,_that.nomi,_that.descrizione,_that.descrizioneBreve,_that.categoria,_that.stile,_that.posizioni,_that.lang,_that.slug,_that.slugs,_that.tradizione,_that.tradizioni,_that.forma,_that.larghezza,_that.larghezzaStretto,_that.carteDaScegliere,_that.mazzo,_that.nCarte,_that.immagine);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String nome,  Map<String, String>? nomi,  String descrizione,  String descrizioneBreve,  String categoria,  String? stile,  List<Posizione> posizioni,  String? lang,  String? slug,  Map<String, String>? slugs,  String? tradizione,  Map<String, String>? tradizioni,  String forma,  double? larghezza,  double? larghezzaStretto,  int? carteDaScegliere,  String mazzo,  int? nCarte, @ImmagineBlogJson()  ImmagineBlog? immagine)  $default,) {final _that = this;
switch (_that) {
case _StesaSezione():
return $default(_that.id,_that.nome,_that.nomi,_that.descrizione,_that.descrizioneBreve,_that.categoria,_that.stile,_that.posizioni,_that.lang,_that.slug,_that.slugs,_that.tradizione,_that.tradizioni,_that.forma,_that.larghezza,_that.larghezzaStretto,_that.carteDaScegliere,_that.mazzo,_that.nCarte,_that.immagine);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String nome,  Map<String, String>? nomi,  String descrizione,  String descrizioneBreve,  String categoria,  String? stile,  List<Posizione> posizioni,  String? lang,  String? slug,  Map<String, String>? slugs,  String? tradizione,  Map<String, String>? tradizioni,  String forma,  double? larghezza,  double? larghezzaStretto,  int? carteDaScegliere,  String mazzo,  int? nCarte, @ImmagineBlogJson()  ImmagineBlog? immagine)?  $default,) {final _that = this;
switch (_that) {
case _StesaSezione() when $default != null:
return $default(_that.id,_that.nome,_that.nomi,_that.descrizione,_that.descrizioneBreve,_that.categoria,_that.stile,_that.posizioni,_that.lang,_that.slug,_that.slugs,_that.tradizione,_that.tradizioni,_that.forma,_that.larghezza,_that.larghezzaStretto,_that.carteDaScegliere,_that.mazzo,_that.nCarte,_that.immagine);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StesaSezione extends StesaSezione {
  const _StesaSezione({required this.id, required this.nome,  Map<String, String>? nomi, this.descrizione = '', this.descrizioneBreve = '', this.categoria = 'standard', this.stile,  List<Posizione> posizioni = const <Posizione>[], this.lang, this.slug,  Map<String, String>? slugs, this.tradizione,  Map<String, String>? tradizioni, this.forma = 'standard', this.larghezza, this.larghezzaStretto, this.carteDaScegliere, this.mazzo = 'completo', this.nCarte, @ImmagineBlogJson() this.immagine}): _nomi = nomi,_posizioni = posizioni,_slugs = slugs,_tradizioni = tradizioni,super._();
  factory _StesaSezione.fromJson(Map<String, dynamic> json) => _$StesaSezioneFromJson(json);

@override final  String id;
@override final  String nome;
 final  Map<String, String>? _nomi;
@override Map<String, String>? get nomi {
  final value = _nomi;
  if (value == null) return null;
  if (_nomi is EqualUnmodifiableMapView) return _nomi;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey() final  String descrizione;
/// La descrizione accorciata (al più 160 caratteri).
@override@JsonKey() final  String descrizioneBreve;
@override@JsonKey() final  String categoria;
@override final  String? stile;
 final  List<Posizione> _posizioni;
@override@JsonKey() List<Posizione> get posizioni {
  if (_posizioni is EqualUnmodifiableListView) return _posizioni;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_posizioni);
}

@override final  String? lang;
@override final  String? slug;
 final  Map<String, String>? _slugs;
@override Map<String, String>? get slugs {
  final value = _slugs;
  if (value == null) return null;
  if (_slugs is EqualUnmodifiableMapView) return _slugs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

/// La tradizione in poche parole («love», «Celtic tradition»), nella lingua dei testi.
@override final  String? tradizione;
/// La tradizione in ogni lingua che ce l'ha.
 final  Map<String, String>? _tradizioni;
/// La tradizione in ogni lingua che ce l'ha.
@override Map<String, String>? get tradizioni {
  final value = _tradizioni;
  if (value == null) return null;
  if (_tradizioni is EqualUnmodifiableMapView) return _tradizioni;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey() final  String forma;
@override final  double? larghezza;
@override final  double? larghezzaStretto;
@override final  int? carteDaScegliere;
@override@JsonKey() final  String mazzo;
@override final  int? nCarte;
@override@ImmagineBlogJson() final  ImmagineBlog? immagine;

/// Create a copy of StesaSezione
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StesaSezioneCopyWith<_StesaSezione> get copyWith => __$StesaSezioneCopyWithImpl<_StesaSezione>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StesaSezioneToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _StesaSezione&&(identical(other.id, id) || other.id == id)&&(identical(other.nome, nome) || other.nome == nome)&&const DeepCollectionEquality().equals(other.nomi, _nomi)&&(identical(other.descrizione, descrizione) || other.descrizione == descrizione)&&(identical(other.descrizioneBreve, descrizioneBreve) || other.descrizioneBreve == descrizioneBreve)&&(identical(other.categoria, categoria) || other.categoria == categoria)&&(identical(other.stile, stile) || other.stile == stile)&&const DeepCollectionEquality().equals(other.posizioni, _posizioni)&&(identical(other.lang, lang) || other.lang == lang)&&(identical(other.slug, slug) || other.slug == slug)&&const DeepCollectionEquality().equals(other.slugs, _slugs)&&(identical(other.tradizione, tradizione) || other.tradizione == tradizione)&&const DeepCollectionEquality().equals(other.tradizioni, _tradizioni)&&(identical(other.forma, forma) || other.forma == forma)&&(identical(other.larghezza, larghezza) || other.larghezza == larghezza)&&(identical(other.larghezzaStretto, larghezzaStretto) || other.larghezzaStretto == larghezzaStretto)&&(identical(other.carteDaScegliere, carteDaScegliere) || other.carteDaScegliere == carteDaScegliere)&&(identical(other.mazzo, mazzo) || other.mazzo == mazzo)&&(identical(other.nCarte, nCarte) || other.nCarte == nCarte)&&(identical(other.immagine, immagine) || other.immagine == immagine));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,nome,const DeepCollectionEquality().hash(_nomi),descrizione,descrizioneBreve,categoria,stile,const DeepCollectionEquality().hash(_posizioni),lang,slug,const DeepCollectionEquality().hash(_slugs),tradizione,const DeepCollectionEquality().hash(_tradizioni),forma,larghezza,larghezzaStretto,carteDaScegliere,mazzo,nCarte,immagine]);
}

@override
String toString() {
    return 'StesaSezione(id: $id, nome: $nome, nomi: $nomi, descrizione: $descrizione, descrizioneBreve: $descrizioneBreve, categoria: $categoria, stile: $stile, posizioni: $posizioni, lang: $lang, slug: $slug, slugs: $slugs, tradizione: $tradizione, tradizioni: $tradizioni, forma: $forma, larghezza: $larghezza, larghezzaStretto: $larghezzaStretto, carteDaScegliere: $carteDaScegliere, mazzo: $mazzo, nCarte: $nCarte, immagine: $immagine)';
}


}

/// @nodoc
abstract mixin class _$StesaSezioneCopyWith<$Res> implements $StesaSezioneCopyWith<$Res> {
  factory _$StesaSezioneCopyWith(_StesaSezione value, $Res Function(_StesaSezione) _then) = __$StesaSezioneCopyWithImpl;
@override @useResult
$Res call({
 String id, String nome, Map<String, String>? nomi, String descrizione, String descrizioneBreve, String categoria, String? stile, List<Posizione> posizioni, String? lang, String? slug, Map<String, String>? slugs, String? tradizione, Map<String, String>? tradizioni, String forma, double? larghezza, double? larghezzaStretto, int? carteDaScegliere, String mazzo, int? nCarte,@ImmagineBlogJson() ImmagineBlog? immagine
});


@override $ImmagineBlogCopyWith<$Res>? get immagine;

}
/// @nodoc
class __$StesaSezioneCopyWithImpl<$Res>
    implements _$StesaSezioneCopyWith<$Res> {
  __$StesaSezioneCopyWithImpl(this._self, this._then);

  final _StesaSezione _self;
  final $Res Function(_StesaSezione) _then;

/// Create a copy of StesaSezione
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nome = null,Object? nomi = freezed,Object? descrizione = null,Object? descrizioneBreve = null,Object? categoria = null,Object? stile = freezed,Object? posizioni = null,Object? lang = freezed,Object? slug = freezed,Object? slugs = freezed,Object? tradizione = freezed,Object? tradizioni = freezed,Object? forma = null,Object? larghezza = freezed,Object? larghezzaStretto = freezed,Object? carteDaScegliere = freezed,Object? mazzo = null,Object? nCarte = freezed,Object? immagine = freezed,}) {
  return _then(_StesaSezione(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,nomi: freezed == nomi ? _self._nomi : nomi // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,descrizione: null == descrizione ? _self.descrizione : descrizione // ignore: cast_nullable_to_non_nullable
as String,descrizioneBreve: null == descrizioneBreve ? _self.descrizioneBreve : descrizioneBreve // ignore: cast_nullable_to_non_nullable
as String,categoria: null == categoria ? _self.categoria : categoria // ignore: cast_nullable_to_non_nullable
as String,stile: freezed == stile ? _self.stile : stile // ignore: cast_nullable_to_non_nullable
as String?,posizioni: null == posizioni ? _self._posizioni : posizioni // ignore: cast_nullable_to_non_nullable
as List<Posizione>,lang: freezed == lang ? _self.lang : lang // ignore: cast_nullable_to_non_nullable
as String?,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,slugs: freezed == slugs ? _self._slugs : slugs // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,tradizione: freezed == tradizione ? _self.tradizione : tradizione // ignore: cast_nullable_to_non_nullable
as String?,tradizioni: freezed == tradizioni ? _self._tradizioni : tradizioni // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,forma: null == forma ? _self.forma : forma // ignore: cast_nullable_to_non_nullable
as String,larghezza: freezed == larghezza ? _self.larghezza : larghezza // ignore: cast_nullable_to_non_nullable
as double?,larghezzaStretto: freezed == larghezzaStretto ? _self.larghezzaStretto : larghezzaStretto // ignore: cast_nullable_to_non_nullable
as double?,carteDaScegliere: freezed == carteDaScegliere ? _self.carteDaScegliere : carteDaScegliere // ignore: cast_nullable_to_non_nullable
as int?,mazzo: null == mazzo ? _self.mazzo : mazzo // ignore: cast_nullable_to_non_nullable
as String,nCarte: freezed == nCarte ? _self.nCarte : nCarte // ignore: cast_nullable_to_non_nullable
as int?,immagine: freezed == immagine ? _self.immagine : immagine // ignore: cast_nullable_to_non_nullable
as ImmagineBlog?,
  ));
}

/// Create a copy of StesaSezione
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ImmagineBlogCopyWith<$Res>? get immagine {
    if (_self.immagine == null) {
    return null;
  }

  return $ImmagineBlogCopyWith<$Res>(_self.immagine!, (value) {
    return _then(_self.copyWith(immagine: value));
  });
}
}


/// @nodoc
mixin _$ElencoArticoli {

 int get totale; int get pagina; int get perPagina; int get pagine; List<ArticoloBreve> get articoli;
/// Create a copy of ElencoArticoli
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ElencoArticoliCopyWith<ElencoArticoli> get copyWith => _$ElencoArticoliCopyWithImpl<ElencoArticoli>(this as ElencoArticoli, _$identity);

  /// Serializes this ElencoArticoli to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ElencoArticoli;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ElencoArticoli&&(identical(other.totale, _this.totale) || other.totale == _this.totale)&&(identical(other.pagina, _this.pagina) || other.pagina == _this.pagina)&&(identical(other.perPagina, _this.perPagina) || other.perPagina == _this.perPagina)&&(identical(other.pagine, _this.pagine) || other.pagine == _this.pagine)&&const DeepCollectionEquality().equals(other.articoli, _this.articoli));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ElencoArticoli;
  return Object.hash(runtimeType,_this.totale,_this.pagina,_this.perPagina,_this.pagine,const DeepCollectionEquality().hash(_this.articoli));
}

@override
String toString() {
  final _this = this as ElencoArticoli;
  return 'ElencoArticoli(totale: ${_this.totale}, pagina: ${_this.pagina}, perPagina: ${_this.perPagina}, pagine: ${_this.pagine}, articoli: ${_this.articoli})';
}


}

/// @nodoc
abstract mixin class $ElencoArticoliCopyWith<$Res>  {
  factory $ElencoArticoliCopyWith(ElencoArticoli value, $Res Function(ElencoArticoli) _then) = _$ElencoArticoliCopyWithImpl;
@useResult
$Res call({
 int totale, int pagina, int perPagina, int pagine, List<ArticoloBreve> articoli
});




}
/// @nodoc
class _$ElencoArticoliCopyWithImpl<$Res>
    implements $ElencoArticoliCopyWith<$Res> {
  _$ElencoArticoliCopyWithImpl(this._self, this._then);

  final ElencoArticoli _self;
  final $Res Function(ElencoArticoli) _then;

/// Create a copy of ElencoArticoli
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? totale = null,Object? pagina = null,Object? perPagina = null,Object? pagine = null,Object? articoli = null,}) {
  return _then(ElencoArticoli(
totale: null == totale ? _self.totale : totale // ignore: cast_nullable_to_non_nullable
as int,pagina: null == pagina ? _self.pagina : pagina // ignore: cast_nullable_to_non_nullable
as int,perPagina: null == perPagina ? _self.perPagina : perPagina // ignore: cast_nullable_to_non_nullable
as int,pagine: null == pagine ? _self.pagine : pagine // ignore: cast_nullable_to_non_nullable
as int,articoli: null == articoli ? _self.articoli : articoli // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,
  ));
}

}


/// Adds pattern-matching-related methods to [ElencoArticoli].
extension ElencoArticoliPatterns on ElencoArticoli {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ElencoArticoli value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ElencoArticoli() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ElencoArticoli value)  $default,){
final _that = this;
switch (_that) {
case _ElencoArticoli():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ElencoArticoli value)?  $default,){
final _that = this;
switch (_that) {
case _ElencoArticoli() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int totale,  int pagina,  int perPagina,  int pagine,  List<ArticoloBreve> articoli)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ElencoArticoli() when $default != null:
return $default(_that.totale,_that.pagina,_that.perPagina,_that.pagine,_that.articoli);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int totale,  int pagina,  int perPagina,  int pagine,  List<ArticoloBreve> articoli)  $default,) {final _that = this;
switch (_that) {
case _ElencoArticoli():
return $default(_that.totale,_that.pagina,_that.perPagina,_that.pagine,_that.articoli);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int totale,  int pagina,  int perPagina,  int pagine,  List<ArticoloBreve> articoli)?  $default,) {final _that = this;
switch (_that) {
case _ElencoArticoli() when $default != null:
return $default(_that.totale,_that.pagina,_that.perPagina,_that.pagine,_that.articoli);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ElencoArticoli implements ElencoArticoli {
  const _ElencoArticoli({this.totale = 0, this.pagina = 1, this.perPagina = 25, this.pagine = 1,  List<ArticoloBreve> articoli = const <ArticoloBreve>[]}): _articoli = articoli;
  factory _ElencoArticoli.fromJson(Map<String, dynamic> json) => _$ElencoArticoliFromJson(json);

@override@JsonKey() final  int totale;
@override@JsonKey() final  int pagina;
@override@JsonKey() final  int perPagina;
@override@JsonKey() final  int pagine;
 final  List<ArticoloBreve> _articoli;
@override@JsonKey() List<ArticoloBreve> get articoli {
  if (_articoli is EqualUnmodifiableListView) return _articoli;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_articoli);
}


/// Create a copy of ElencoArticoli
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ElencoArticoliCopyWith<_ElencoArticoli> get copyWith => __$ElencoArticoliCopyWithImpl<_ElencoArticoli>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ElencoArticoliToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ElencoArticoli&&(identical(other.totale, totale) || other.totale == totale)&&(identical(other.pagina, pagina) || other.pagina == pagina)&&(identical(other.perPagina, perPagina) || other.perPagina == perPagina)&&(identical(other.pagine, pagine) || other.pagine == pagine)&&const DeepCollectionEquality().equals(other.articoli, _articoli));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,totale,pagina,perPagina,pagine,const DeepCollectionEquality().hash(_articoli));
}

@override
String toString() {
    return 'ElencoArticoli(totale: $totale, pagina: $pagina, perPagina: $perPagina, pagine: $pagine, articoli: $articoli)';
}


}

/// @nodoc
abstract mixin class _$ElencoArticoliCopyWith<$Res> implements $ElencoArticoliCopyWith<$Res> {
  factory _$ElencoArticoliCopyWith(_ElencoArticoli value, $Res Function(_ElencoArticoli) _then) = __$ElencoArticoliCopyWithImpl;
@override @useResult
$Res call({
 int totale, int pagina, int perPagina, int pagine, List<ArticoloBreve> articoli
});




}
/// @nodoc
class __$ElencoArticoliCopyWithImpl<$Res>
    implements _$ElencoArticoliCopyWith<$Res> {
  __$ElencoArticoliCopyWithImpl(this._self, this._then);

  final _ElencoArticoli _self;
  final $Res Function(_ElencoArticoli) _then;

/// Create a copy of ElencoArticoli
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? totale = null,Object? pagina = null,Object? perPagina = null,Object? pagine = null,Object? articoli = null,}) {
  return _then(_ElencoArticoli(
totale: null == totale ? _self.totale : totale // ignore: cast_nullable_to_non_nullable
as int,pagina: null == pagina ? _self.pagina : pagina // ignore: cast_nullable_to_non_nullable
as int,perPagina: null == perPagina ? _self.perPagina : perPagina // ignore: cast_nullable_to_non_nullable
as int,pagine: null == pagine ? _self.pagine : pagine // ignore: cast_nullable_to_non_nullable
as int,articoli: null == articoli ? _self._articoli : articoli // ignore: cast_nullable_to_non_nullable
as List<ArticoloBreve>,
  ));
}


}


/// @nodoc
mixin _$EtichettaConConteggio {

 String get slug; String get nome; int get n;
/// Create a copy of EtichettaConConteggio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EtichettaConConteggioCopyWith<EtichettaConConteggio> get copyWith => _$EtichettaConConteggioCopyWithImpl<EtichettaConConteggio>(this as EtichettaConConteggio, _$identity);

  /// Serializes this EtichettaConConteggio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as EtichettaConConteggio;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EtichettaConConteggio&&(identical(other.slug, _this.slug) || other.slug == _this.slug)&&(identical(other.nome, _this.nome) || other.nome == _this.nome)&&(identical(other.n, _this.n) || other.n == _this.n));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as EtichettaConConteggio;
  return Object.hash(runtimeType,_this.slug,_this.nome,_this.n);
}

@override
String toString() {
  final _this = this as EtichettaConConteggio;
  return 'EtichettaConConteggio(slug: ${_this.slug}, nome: ${_this.nome}, n: ${_this.n})';
}


}

/// @nodoc
abstract mixin class $EtichettaConConteggioCopyWith<$Res>  {
  factory $EtichettaConConteggioCopyWith(EtichettaConConteggio value, $Res Function(EtichettaConConteggio) _then) = _$EtichettaConConteggioCopyWithImpl;
@useResult
$Res call({
 String slug, String nome, int n
});




}
/// @nodoc
class _$EtichettaConConteggioCopyWithImpl<$Res>
    implements $EtichettaConConteggioCopyWith<$Res> {
  _$EtichettaConConteggioCopyWithImpl(this._self, this._then);

  final EtichettaConConteggio _self;
  final $Res Function(EtichettaConConteggio) _then;

/// Create a copy of EtichettaConConteggio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? slug = null,Object? nome = null,Object? n = null,}) {
  return _then(EtichettaConConteggio(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,n: null == n ? _self.n : n // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [EtichettaConConteggio].
extension EtichettaConConteggioPatterns on EtichettaConConteggio {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EtichettaConConteggio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EtichettaConConteggio() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EtichettaConConteggio value)  $default,){
final _that = this;
switch (_that) {
case _EtichettaConConteggio():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EtichettaConConteggio value)?  $default,){
final _that = this;
switch (_that) {
case _EtichettaConConteggio() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String slug,  String nome,  int n)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EtichettaConConteggio() when $default != null:
return $default(_that.slug,_that.nome,_that.n);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String slug,  String nome,  int n)  $default,) {final _that = this;
switch (_that) {
case _EtichettaConConteggio():
return $default(_that.slug,_that.nome,_that.n);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String slug,  String nome,  int n)?  $default,) {final _that = this;
switch (_that) {
case _EtichettaConConteggio() when $default != null:
return $default(_that.slug,_that.nome,_that.n);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EtichettaConConteggio implements EtichettaConConteggio {
  const _EtichettaConConteggio({required this.slug, required this.nome, this.n = 0});
  factory _EtichettaConConteggio.fromJson(Map<String, dynamic> json) => _$EtichettaConConteggioFromJson(json);

@override final  String slug;
@override final  String nome;
@override@JsonKey() final  int n;

/// Create a copy of EtichettaConConteggio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EtichettaConConteggioCopyWith<_EtichettaConConteggio> get copyWith => __$EtichettaConConteggioCopyWithImpl<_EtichettaConConteggio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EtichettaConConteggioToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _EtichettaConConteggio&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.nome, nome) || other.nome == nome)&&(identical(other.n, n) || other.n == n));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,slug,nome,n);
}

@override
String toString() {
    return 'EtichettaConConteggio(slug: $slug, nome: $nome, n: $n)';
}


}

/// @nodoc
abstract mixin class _$EtichettaConConteggioCopyWith<$Res> implements $EtichettaConConteggioCopyWith<$Res> {
  factory _$EtichettaConConteggioCopyWith(_EtichettaConConteggio value, $Res Function(_EtichettaConConteggio) _then) = __$EtichettaConConteggioCopyWithImpl;
@override @useResult
$Res call({
 String slug, String nome, int n
});




}
/// @nodoc
class __$EtichettaConConteggioCopyWithImpl<$Res>
    implements _$EtichettaConConteggioCopyWith<$Res> {
  __$EtichettaConConteggioCopyWithImpl(this._self, this._then);

  final _EtichettaConConteggio _self;
  final $Res Function(_EtichettaConConteggio) _then;

/// Create a copy of EtichettaConConteggio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? slug = null,Object? nome = null,Object? n = null,}) {
  return _then(_EtichettaConConteggio(
slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,nome: null == nome ? _self.nome : nome // ignore: cast_nullable_to_non_nullable
as String,n: null == n ? _self.n : n // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
